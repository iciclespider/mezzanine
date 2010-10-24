
from django.conf import settings
from django.conf.urls.defaults import *
from mezzanine.settings import global_settings


urlpatterns = patterns("",
    ("^", include("mezzanine.core.urls")),
)

if "mezzanine.blog" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^%s/" % global_settings.BLOG_SLUG, include("mezzanine.blog.urls")),
    )
if "mezzanine.pages" in settings.INSTALLED_APPS:
    urlpatterns += patterns("",
        ("^", include("mezzanine.pages.urls")),
    )
