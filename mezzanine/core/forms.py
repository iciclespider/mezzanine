
from uuid import uuid4

from django.forms import models, fields, widgets
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from mezzanine.utils.urls import content_media_urls
from mezzanine.core.models import Orderable


class OrderWidget(widgets.HiddenInput):
    """
    Add up and down arrows for ordering controls next to a hidden form field.
    """
    def render(self, *args, **kwargs):
        rendered = super(OrderWidget, self).render(*args, **kwargs)
        arrows = ["<img src='%simg/admin/arrow-%s.gif' />" %
            (settings.ADMIN_MEDIA_PREFIX, arrow) for arrow in ("up", "down")]
        arrows = "<span class='ordering'>%s</span>" % "".join(arrows)
        return rendered + mark_safe(arrows)


class DynamicInlineAdminForm(models.ModelForm):
    """
    Form for ``DynamicInlineAdmin`` that can be collapsed and sorted with 
    drag and drop using ``OrderWidget``.
    """

    class Media:
        js = content_media_urls("js/jquery-ui-1.8.1.custom.min.js",
                                "js/dynamic_inline.js",)

    def __init__(self, *args, **kwargs):
        super(DynamicInlineAdminForm, self).__init__(*args, **kwargs)
        if issubclass(self._meta.model, Orderable):
            self.fields["_order"] = fields.CharField(label=_("Order"),
                widget=OrderWidget, required=False)


def get_edit_form(obj, field_names, data=None, files=None):
    """
    Returns the in-line editing form for editing a single model field.
    """

    class EditForm(models.ModelForm):
        """
        In-line editing form for editing a single model field.
        """

        app = fields.CharField(widget=widgets.HiddenInput)
        model = fields.CharField(widget=widgets.HiddenInput)
        id = fields.CharField(widget=widgets.HiddenInput)
        fields = fields.CharField(widget=widgets.HiddenInput)

        class Meta:
            model = obj.__class__
            fields = field_names.split(",")

        def __init__(self, *args, **kwargs):
            super(EditForm, self).__init__(*args, **kwargs)
            self.uuid = str(uuid4())
            for f in self.fields.keys():
                self.fields[f].widget.attrs["id"] = "%s-%s" % (f, self.uuid)

    initial = {"app": obj._meta.app_label, "id": obj.id, "fields": field_names,
        "model": obj._meta.object_name.lower()}
    return EditForm(instance=obj, initial=initial, data=data, files=files)
