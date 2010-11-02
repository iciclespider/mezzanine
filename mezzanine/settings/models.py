
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mezzanine.settings import registry, editables


class Settings(models.Model):
    """
    A named group of settings.
    """
    name = models.CharField(max_length=50)

    class Meta(object):
        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'


    def editables(self, names=None):
        return editables()

    def __getattr__(self, name):
        registry_setting = registry.get(name, None)
        if not registry_setting:
            raise AttributeError("Setting does not exist: %s" % name)
        try:
            setting = self.settings.get(name=name)
            registry_type = registry_setting["type"]
            if registry_type is bool:
                value = setting.value != "False"
            else:
                value = registry_type(setting.value)
        except Setting.DoesNotExist:
            value = registry_setting["default"]
        self.__dict__[name] = value
        return getattr(self, name)

    def __setattr__(self, name, value):
        registry_setting = registry.get(name, None)
        if not registry_setting:
            self.__dict__[name] = value
            return
        if not registry_setting["editable"]:
            raise AttributeError("Read only setting value: %s" % name)
        self_value = self.__dict__.get(name, registry_setting["default"])
        if value == self_value:
            return
        if value is None:
            self.settings.filter(name=name).delete()
        else:
            try:
                setting = self.settings.get(name=name)
                setting.value = value
                setting.save()
            except Setting.DoesNotExist:
                self.settings.create(name=name, value=value)
        self.__dict__[name] = value

    def __unicode__(self):
        return unicode(self.name)

class Setting(models.Model):
    """
    Stores values for ``mezzanine.settings`` that can be edited via the admin.
    """
    settings = models.ForeignKey(Settings, related_name="settings")
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=2000)

    class Meta:
        verbose_name = _("Setting")
        verbose_name_plural = _("Settings")

    def __unicode__(self):
        return unicode(self.name)

class SiteSettings(models.Model):
    """
    Associate a set of settings to a site.
    """
    site = models.OneToOneField(Site, related_name="setting")
    settings = models.ForeignKey(Settings, related_name="sites")

    class Meta:
        verbose_name = _("Site settings")
        verbose_name_plural = _("Site settings")

    def __unicode__(self):
        return unicode(self.settings.name)
