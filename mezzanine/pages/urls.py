
from django.conf import settings
from django.conf.urls.defaults import patterns, url

# Page patterns.
urlpatterns = patterns("mezzanine.pages.views",
    url("^(.*)$", "page"),
)
