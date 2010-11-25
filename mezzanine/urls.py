
from django.conf import settings
from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from mezzanine.configuration import global_settings

admin.autodiscover()

handler404 = 'mezzanine.core.views.handler_404'
handler500 = 'mezzanine.core.views.handler_500'

urlpatterns = patterns("",
    ("^", include("mezzanine.core.urls")),
    ("^", include("mezzanine.pages.urls")),
    ("^admin/filebrowser/", include("filebrowser.urls")),
    ("^admin/", include(admin.site.urls)),
    ("^grappelli/", include("grappelli.urls")),
)
