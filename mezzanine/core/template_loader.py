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
            return (Template.objects.get(name=name).content, name)
        except Template.DoesNotExist:
            raise TemplateDoesNotExist(name)
