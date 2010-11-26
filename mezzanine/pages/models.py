
from django.core.urlresolvers import resolve
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.models import Displayable, Orderable, Content
from mezzanine.pages.managers import PageManager
from mezzanine.utils import admin_url

class Page(Orderable, Displayable):
    """
    A page in the page tree.
    """

    parent = models.ForeignKey("Page", blank=True, null=True,
        related_name="children")
    menu_name = models.CharField(_("Menu Name"), max_length=100, blank=True)
    in_navigation = models.BooleanField(_("Show in navigation"), default=True)
    in_footer = models.BooleanField(_("Show in footer"))
    titles = models.CharField(editable=False, max_length=1000, null=True)
    content_model = models.CharField(editable=False, max_length=50, null=True)
    login_required = models.BooleanField(_("Login required"),
        help_text=_("If checked, only logged in users can view this page"))
    template = models.CharField(max_length=100, blank=True)

    objects = PageManager()

    class Meta(Orderable.Meta, Displayable.Meta):
        abstract = False
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ("parent__id", "_order")
        order_with_respect_to = "parent"

    def __unicode__(self):
        return self.titles

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)

    @property
    def instance(self):
        if self.content_model and self.content_model != self._meta.object_name.lower():
            instance = getattr(self, self.content_model, None)
            if instance:
                return instance
        return self

    def __eq__(self, other):
        return isinstance(other, Page) and self.instance._get_pk_val() == other.instance._get_pk_val()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.instance._get_pk_val())

    @models.permalink
    def get_absolute_url(self):
        return ("page", (), {"slug": self.get_slug()})

    def get_admin_url(self):
        return admin_url(self, "change", self.id)

    def save(self, *args, **kwargs):
        """
        Create the titles field using the titles up the parent chain and set
        the initial value for ordering.
        """
        if self.parent:
            self.settings = self.parent.settings
        if self.id is None:
            self.content_model = self._meta.object_name.lower()
        titles = [self.title]
        parent = self.parent
        while parent is not None:
            titles.insert(0, parent.title)
            parent = parent.parent
        self.titles = " / ".join(titles)
        super(Page, self).save(*args, **kwargs)

    def get_content_model(self):
        return getattr(self, self.content_model, None)

    def get_slug(self):
        """
        Recursively build the slug from the chain of parents.
        """
        if not self.parent:
            return ''
        slug = self.parent.get_slug()
        if slug:
            slug += '/'
        return slug + slugify(self.title)

    def overridden(self):
        """
        Return True if the page's slug has an explicitly defined url pattern
        and is therefore considered to be overriden.
        """
        from mezzanine.pages.views import page
        resolved_view = resolve(self.get_absolute_url())[0]
        return resolved_view != page

    def get_template(self):
        if self.template:
            return self.template
        return self.instance.get_default_template()

    def get_default_template(self):
        return self.settings.TEMPLATE_PAGE


class ContentPage(Page, Content):
    """
    Implements the default type of page with a single HTML content field.
    """

    class Meta(Page.Meta, Content.Meta):
        abstract = False
        verbose_name = _("Content page")
        verbose_name_plural = _("Content pages")

    def get_default_template(self):
        return self.settings.TEMPLATE_CONTENTPAGE
