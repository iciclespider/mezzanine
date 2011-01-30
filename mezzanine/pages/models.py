
from django.db import models
from django.http import HttpResponse, Http404
from django.template import RequestContext, Template
from django.template.loader import get_template
from mezzanine.configuration.models import Settings
from mezzanine.core.fields import HtmlField
from mezzanine.core.models import Displayable, Orderable, Content
from mezzanine.pages.managers import PageManager
from mezzanine.utils.urls import admin_url

class Page(Orderable, Displayable):
    """
    A page in the page tree.
    """

    settings = models.ForeignKey(Settings, related_name="pages")
    parent = models.ForeignKey("Page", blank=True, null=True,
        related_name="children")
    menu_name = models.CharField("Menu Name", max_length=100, blank=True)
    in_navigation = models.BooleanField("Show in navigation", default=True)
    in_footer = models.BooleanField("Show in footer")
    content_model = models.CharField(editable=False, max_length=50, null=True)
    login_required = models.BooleanField("Login required",
        help_text="If checked, only logged in users can view this page")
    style = HtmlField("Style", widget_rows=20, blank=True)
    template = HtmlField("Template", widget_rows=40, blank=True)

    objects = PageManager()

    class Meta(Orderable.Meta, Displayable.Meta):
        abstract = False
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        ordering = ("parent__id", "_order")
        order_with_respect_to = "parent"
        unique_together = ("settings", "parent", "slug")

    def __unicode__(self):
        return self.head_title

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

    def get_admin_url(self):
        return admin_url(self, "change", self.id)

    def save(self, *args, **kwargs):
        if self.parent:
            self.settings = self.parent.settings
        if self.id is None:
            self.content_model = self._meta.object_name.lower()
        super(Page, self).save(*args, **kwargs)

    def generate_slug(self):
        if (not self.parent):
            return ''
        qs = self.parent.children.all()
        if self.id is not None:
            qs = qs.exclude(id=self.id)
        base = super(Page, self).generate_slug()
        slug = base
        i = 0
        while True:
            try:
                qs.get(slug=slug)
            except Page.DoesNotExist:
                return slug
            i += 1
            slug = base + '-' + str(i)

    def get_content_model(self):
        return getattr(self, self.content_model, None)

    @property
    def url(self):
        return self.instance.get_url()

    def get_url(self):
        if not self.parent:
            return '/'
        return self.parent.get_url() + self.slug + '/'

    @property
    def head_title(self):
        title = super(Page, self).head_title
        if self.parent:
            title = self.parent.head_title + ' / ' + title
        return title

    def response(self, request, url):
        return self.instance.get_response(request, url)

    def get_response(self, request, url):
        if not url:
            return self.render(request)
        ix = url.find('/')
        if ix >= 0:
            slug = url[:ix]
            url = url[ix + 1:]
        else:
            slug = url
            url = ''
        return self.get_child_response(request, slug, url)

    def render(self, request):
        context = self.get_context(request)
        if context:
            context['displayable'] = self.instance
        else:
            context = {'displayable':self.instance}
        return HttpResponse(self.get_template().render(RequestContext(request, context)))

    def get_child_response(self, request, slug, url):
        try:
            child = self.children.get(slug=slug)
        except Page.DoesNotExist:
            raise Http404
        except Page.MultipleObjectsReturned:
            raise Http404
        return child.response(request, url)

    def get_template(self):
        if self.template:
            return Template(self.template, name='"%s" Page template' % self.head_title)
        return get_template(self.instance.default_template)

    @property
    def default_template(self):
        return self.settings.TEMPLATE_PAGE

    def get_context(self, request):
        return None


class ContentPage(Page, Content):
    """
    Implements the default type of page with a single HTML content field.
    """

    class Meta(Page.Meta, Content.Meta):
        abstract = False
        verbose_name = "Content page"
        verbose_name_plural = "Content pages"

    @property
    def default_template(self):
        return self.settings.TEMPLATE_CONTENTPAGE
