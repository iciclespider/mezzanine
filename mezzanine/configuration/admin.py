
from django.contrib import admin
from django.contrib.sites.models import Site
from mezzanine.configuration import editables
from mezzanine.configuration.forms import SettingsForm
from mezzanine.configuration.models import Settings, SiteSettings


class SettingsAdmin(admin.ModelAdmin):
    """
    Admin class for settings model.
    """
    list_display = ('name',)
    form = SettingsForm

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(SettingsAdmin, self).get_fieldsets(request, obj)
        if obj:
            fields = obj.editables()
        else:
            fields = editables()
        fields.sort()
        fieldsets[0][1]['fields'].extend(fields)
        return fieldsets

class SiteSettingsInline(admin.TabularInline):
    model = SiteSettings
    verbose_name = 'Settings'
    verbose_name_plural = 'Settings'

class SiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name')
    search_fields = ('domain', 'name')
    inlines = (SiteSettingsInline,)


admin.site.register(Settings, SettingsAdmin)
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)
