
from django.db import models
from django.utils.safestring import mark_safe


class HtmlField(models.TextField):
    """
    TextField that stores HTML.
    """
    __metaclass__ = models.SubfieldBase

    def formfield(self, **kwargs):
        """
        Apply the class to the widget that will render the field as a
        TincyMCE Editor.
        """
        formfield = super(HtmlField, self).formfield(**kwargs)
        formfield.widget.attrs["class"] = "mceEditor"
        return formfield

    def to_python(self, value):
        return mark_safe(value)

