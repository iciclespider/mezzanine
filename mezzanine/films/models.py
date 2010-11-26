
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
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class StaffPage(Page):

    class Meta(Page.Meta):
        abstract = False
        verbose_name = 'Staff page'
        verbose_name_plural = 'Staff pages'

    summary = HtmlField(blank=True)
    members = models.ManyToManyField(Person, through='Member')

    def __unicode__(self):
        return self.menu_name

class Member(Orderable):

    class Meta(Orderable.Meta):
        abstract = False
        verbose_name = "Member"
        verbose_name_plural = "Members"
        order_with_respect_to = "page"

    page = models.ForeignKey(StaffPage)
    person = models.ForeignKey(Person)
    role = models.CharField(max_length=100, blank=True)
    description = HtmlField(widget_rows=5, blank=True)
