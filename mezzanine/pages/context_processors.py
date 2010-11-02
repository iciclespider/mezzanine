
from mezzanine.pages import models

class Template(object):
    def __getitem__(self, key):
        try:
            template = models.Template.objects.get(name=key)
        except models.Template.DoesNotExist:
            raise KeyError('Template "%s" does not exist.' % key)
        return template.content

_template = {"template": Template()}

def template(request):
    return _template
