
from django.conf import settings
import sys

registry = {}

def register_setting(name="", editable=False, description="", default=None):
    """
    Registers a setting that can be edited via the admin.
    """
    default = getattr(settings, "MEZZANINE_%s" % name, default)
    registry[name] = {"name": name, "description": description, "editable":
        editable, "default": default, "type": type(default)}

for app in settings.INSTALLED_APPS:
    try:
        __import__("%s.defaults" % app)
    except ImportError:
        pass

def editables(names=None):
    if names is None:
        names = registry.keys()
    return [k for (k, v) in registry.items() if v["editable"] and k in names]

class GlobalSettings(object):
    def __getattr__(self, name):
        setting = registry.get(name, None)
        if not setting:
            AttributeError("Setting does not exist: %s" % name)
        self.__dict__[name] = setting["default"]
        return getattr(self, name)

global_settings = GlobalSettings()
