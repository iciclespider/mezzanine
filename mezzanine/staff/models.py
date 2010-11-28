
from django.db import models
from mezzanine.core.fields import HtmlField
from mezzanine.core.models import Orderable
from mezzanine.pages.models import Page

class Person(models.Model):

    class Meta(object):
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = ("name",)

    name = models.CharField(max_length=100)
    biography = HtmlField(blank=True)
    photograph = models.ImageField(upload_to='persons/photograph', blank=True)
    website_url = models.URLField("Website URL", blank=True)
    website_name = models.CharField("Website Name", max_length=100, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class StaffPage(Page):

    class Meta(Page.Meta):
        abstract = False
        verbose_name = 'Staff Page'
        verbose_name_plural = 'Staff Pages'

    summary = HtmlField(blank=True)
    people = models.ManyToManyField(Person, related_name="staffs", through='Member')

    def __unicode__(self):
        return self.menu_name

    @property
    def default_template(self):
        return self.settings.TEMPLATE_STAFFPAGE


class Member(Orderable):

    class Meta(Orderable.Meta):
        abstract = False
        verbose_name = "Member"
        verbose_name_plural = "Members"
        ordering = ("page", "_order")
        order_with_respect_to = "page"

    page = models.ForeignKey(StaffPage, related_name="members")
    person = models.ForeignKey(Person, related_name="members")
    role = models.CharField(max_length=100, blank=True)
    description = HtmlField(widget_rows=5, blank=True)
