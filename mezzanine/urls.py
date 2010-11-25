
from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from mezzanine.configuration import global_settings

admin.autodiscover()

handler404 = 'mezzanine.core.views.handler_404'
handler500 = 'mezzanine.core.views.handler_500'

urlpatterns = patterns("",
    url("^admin/page_ordering/$", "mezzanine.pages.views.admin_page_ordering",
        name="admin_page_ordering"),
    url("^admin/keywords_submit/$", "mezzanine.core.views.admin_keywords_submit",
        name="admin_keywords_submit"),
    ("^admin/filebrowser/", include("filebrowser.urls")),
    ("^admin/", include(admin.site.urls)),
    ("^grappelli/", include("grappelli.urls")),
    ("^", include("mezzanine.core.urls")),
    ("^", include("mezzanine.pages.urls")),
)
