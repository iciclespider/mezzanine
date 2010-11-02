
from django.db import models


class HtmlField(models.TextField):
    """
    TextField that stores HTML.
    """
    #__metaclass__ = models.SubfieldBase

    def formfield(self, **kwargs):
        """
        Apply the class to the widget that will render the field as a
        TincyMCE Editor.
        """
        formfield = super(HtmlField, self).formfield(**kwargs)
        formfield.widget.attrs["cols"] = "120"
        formfield.widget.attrs["rows"] = "40"
        formfield.widget.attrs["class"] = "mceEditor"
        return formfield
