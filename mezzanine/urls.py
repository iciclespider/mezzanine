
from django.conf import settings
from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from mezzanine.configuration import global_settings

admin.autodiscover()

urlpatterns = patterns("",
    ("^admin/filebrowser/", include("filebrowser.urls")),
    ("^admin/", include(admin.site.urls)),
    ("^grappelli/", include("grappelli.urls")),
    ("^", include("mezzanine.core.urls")),
    ("^", include("mezzanine.pages.urls")),
)
