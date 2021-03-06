
from datetime import datetime
from django.db import models
from django.db.models.base import ModelBase
from django.template.defaultfilters import slugify, truncatewords_html
from mezzanine.core.fields import HtmlField
from mezzanine.core.managers import (DisplayableManager, KeywordManager,
    TemplateManager)
from mezzanine.utils.models import base_concrete_model


class Slugged(models.Model):
    """
    Abstract model that handles auto-generating slugs.
    """

    slug = models.CharField("URL", max_length=100, blank=True)
    title = models.CharField("Title", max_length=100)

    class Meta:
        abstract = True
        ordering = ("title",)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Create a unique slug from the title by appending an index.
        """
        if not self.slug:
            self.slug = self.generate_slug()
        super(Slugged, self).save(*args, **kwargs)

    def natural_key(self):
        return (self.slug,)

    def generate_slug(self):
        return slugify(self.title)


CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, "Draft"),
    (CONTENT_STATUS_PUBLISHED, "Published"),
)

class Displayable(Slugged):
    """
    Abstract model that provides features of a visible page on the website
    such as publishing fields and meta data.
    """

    status = models.IntegerField("Status",
        choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED)
    publish_date = models.DateTimeField("Published from",
        help_text="With published selected, won't be shown until this time",
        blank=True, null=True)
    expiry_date = models.DateTimeField("Expires on",
        help_text="With published selected, won't be shown after this time",
        blank=True, null=True)
    description = HtmlField("Description", blank=True)
    keywords = models.ManyToManyField("Keyword", verbose_name="Keywords",
        blank=True)
    _keywords = models.CharField(max_length=500, editable=False)
    short_url = models.URLField(blank=True, null=True)

    objects = DisplayableManager()
    search_fields = {"_keywords": 10, "title": 5}

    class Meta(Slugged.Meta):
        abstract = True

    def save(self, *args, **kwargs):
        """
        Set default for ``publsh_date`` and ``description`` if none given.
        """
        if self.publish_date is None:
            # publish_date will be blank when a blog post is created from the
            # quick blog form in the admin dashboard.
            self.publish_date = datetime.now()
        if not self.description:
            self.description = self.description_from_content()
        super(Displayable, self).save(*args, **kwargs)

    @property
    def head_title(self):
        return self.title

    def description_from_content(self):
        """
        Returns the first paragraph of the first content-like field.
        """
        description = ""
        # Get the value of the first HTMLField, or TextField if none found.
        for field_type in (HtmlField, models.TextField):
            if not description:
                for field in self._meta.fields:
                    if isinstance(field, field_type) and \
                        field.name != "description":
                        description = getattr(self, field.name)
                        if description:
                            break
        # Fall back to the title if description couldn't be determined.
        if not description:
            description = self.title
        # Strip everything after the first paragraph or sentence.
        for end in ("</p>", "<br />", "\n", ". "):
            if end in description:
                description = description.split(end)[0] + end
                break
        else:
            description = truncatewords_html(description, 100)
        return description

    def set_searchable_keywords(self):
        """
        Stores the keywords as a single string into the ``_keywords`` field
        for convenient access when searching.
        """
        self._keywords = " ".join([kw.title for kw in self.keywords.all()])
        self.save()

    def admin_link(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), "View on site")
    admin_link.allow_tags = True
    admin_link.short_description = ""


class Content(models.Model):
    """
    Provides a HTML field for managing general content and making it searchable.
    """

    content = HtmlField("Content", widget_rows=40, blank=True)

    search_fields = ("content",)

    class Meta:
        abstract = True


class OrderableBase(ModelBase):
    """
    Checks for ``order_with_respect_to`` on the model's inner ``Meta`` class
    and if found, copies it to a custom attribute and deletes it since it
    will cause errors when used with ``ForeignKey("self")``. Also creates the
    ``ordering`` attribute on the ``Meta`` class if not yet provided.
    """

    def __new__(cls, name, bases, attrs):
        if "Meta" not in attrs:
            class Meta:
                pass
            attrs["Meta"] = Meta
        if hasattr(attrs["Meta"], "order_with_respect_to"):
            attrs["order_with_respect_to"] = attrs["Meta"].order_with_respect_to
            del attrs["Meta"].order_with_respect_to
        if not hasattr(attrs["Meta"], "ordering"):
            setattr(attrs["Meta"], "ordering", ("_order",))
        return super(OrderableBase, cls).__new__(cls, name, bases, attrs)


class Orderable(models.Model):
    """
    Abstract model that provides a custom ordering integer field similar to
    using Meta's ``order_with_respect_to``, since to date (Django 1.2) this
    doesn't work with ``ForeignKey("self")``. We may also want this feature
    for models that aren't ordered with respect to a particular field.
    """

    __metaclass__ = OrderableBase

    _order = models.IntegerField("Order", null=True)

    class Meta:
        abstract = True

    def with_respect_to(self):
        """
        Returns a dict to use as a filter for ordering operations containing
        the original ``Meta.order_with_respect_to`` value if provided.
        """
        try:
            field = self.order_with_respect_to
            return {field: getattr(self, field)}
        except AttributeError:
            return {}

    def save(self, *args, **kwargs):
        """
        Set the initial ordering value.
        """
        if self._order is None:
            lookup = self.with_respect_to()
            concrete_model = base_concrete_model(Orderable, self)
            self._order = concrete_model.objects.filter(**lookup).count() # IGNORE:E1103
        super(Orderable, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Update the ordering values for siblings.
        """
        lookup = self.with_respect_to()
        lookup["_order__gte"] = self._order
        concrete_model = base_concrete_model(Orderable, self)
        after = concrete_model.objects.filter(**lookup) # IGNORE:E1103
        after.update(_order=models.F("_order") - 1)
        super(Orderable, self).delete(*args, **kwargs)


class Ownable(models.Model):
    """
    Abstract model that provides ownership of an object for a user.
    """

    user = models.ForeignKey("auth.User", verbose_name="Author",
        related_name="%(class)ss")

    class Meta:
        abstract = True

    def is_editable(self, request):
        """
        Restrict in-line editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or request.user.id == self.user_id


class Keyword(Slugged):
    """
    Keywords/tags which are managed via a custom Javascript based widget in the
    admin.
    """

    objects = KeywordManager()

    class Meta(Slugged.Meta):
        abstract = False
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"


class Template(Content):
    """
    Implements data base backed django templates.
    """

    directory = models.CharField("Directory", max_length=100, blank=True, db_index=True)
    name = models.CharField("Name", max_length=100, db_index=True)
    extension = models.CharField("Extension", max_length=100, blank=True, db_index=True)

    objects = TemplateManager()

    class Meta(Content.Meta):
        abstract = False
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ("directory", "name", "extension")
        unique_together = (("directory", "name", "extension"),)

    @property
    def full_name(self):
        if self.directory:
            name = self.directory + '/'
        else:
            name = ''
        name += self.name
        if self.extension:
            name += '.' + self.extension
        return name

    def __unicode__(self):
        return self.full_name
