"""
Wrapper for loading templates from the Template model.
"""

from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
from mezzanine.core.models import Template

class Loader(BaseLoader):
    is_usable = True

    def load_template_source(self, name, dirs=None):
        try:
            i = name.rfind('/')
            if i < 0:
                directory = ''
            else:
                directory = name[0:i]
                name = name[i + 1:]
            i = name.rfind('.')
            if i < 0:
                extension = ''
            else:
                extension = name[i + 1:]
                name = name[0:i]
            return (Template.objects.get(directory=directory, name=name, extension=extension).content, name)
        except Template.DoesNotExist:
            raise TemplateDoesNotExist(name)
