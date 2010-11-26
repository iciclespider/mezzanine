
from django.db import models


class HtmlField(models.TextField):
    """
    TextField that stores HTML.
    """
    #__metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.widget_rows = kwargs.pop('widget_rows', 10)
        super(HtmlField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Apply the class to the widget that will render the field as a
        TincyMCE Editor.
        """
        formfield = super(HtmlField, self).formfield(**kwargs)
        formfield.widget.attrs["cols"] = "120"
        formfield.widget.attrs["rows"] = self.widget_rows
        formfield.widget.attrs["class"] = "mceEditor"
        return formfield
