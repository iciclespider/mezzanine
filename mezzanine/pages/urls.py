
from django.conf import settings
from django.conf.urls.defaults import patterns, url

# Page patterns.
urlpatterns = patterns("mezzanine.pages.views",
    url("^$", "home", name="home"),
    url("^admin_page_ordering/$", "admin_page_ordering",
        name="admin_page_ordering"),
    url("^(?P<slug>.*)/$", "page", name="page"),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
