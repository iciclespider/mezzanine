
from django.conf import settings
from django.conf.urls.defaults import patterns, url

# Page patterns.
urlpatterns = patterns("mezzanine.pages.views",
    url("^$", "home", name="home"),
    url("^(?P<slug>.*)/$", "page", name="page"),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
