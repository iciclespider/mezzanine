
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from mezzanine.configuration import global_settings
from urlparse import urlsplit


urlpatterns = patterns("mezzanine.core.views",
    url("^edit/$", "edit", name="edit"),
    url("^search/$", "search", name="search"),
    url("^404/(.*)$", "force_404", name="404"),
    url("^500/(.*)$", "force_500", name="500"),
)

urlpatterns += patterns("",
    ("^%s/(?P<path>.*)$" % global_settings.CONTENT_MEDIA_URL.strip("/"),
        "django.views.static.serve",
        {"document_root": global_settings.CONTENT_MEDIA_PATH}),
)

# Remove unwanted models from the admin that are installed by default with
# third-party apps.
for model in global_settings.ADMIN_REMOVAL:
    try:
        model = tuple(model.rsplit(".", 1))
        exec "from %s import %s" % model
    except ImportError:
        pass
    else:
        try:
            admin.site.unregister(eval(model[1]))
        except NotRegistered:
            pass

# Pairs of optional app names and their urlpatterns.
OPTIONAL_APP_PATTERNS = []
if getattr(settings, "PACKAGE_NAME_FILEBROWSER", None):
    OPTIONAL_APP_PATTERNS.append(
    (settings.PACKAGE_NAME_FILEBROWSER, patterns("",
        ("^admin/filebrowser/", include("%s.urls" %
            settings.PACKAGE_NAME_FILEBROWSER)),
        ("^%s/(?P<path>.*)$" % getattr(settings,
            "FILEBROWSER_URL_FILEBROWSER_MEDIA", "").strip("/"),
            "django.views.static.serve", {'document_root':
            getattr(settings, "FILEBROWSER_PATH_FILEBROWSER_MEDIA", "")}),
    )))
if getattr(settings, "PACKAGE_NAME_GRAPPELLI", None):
    OPTIONAL_APP_PATTERNS.append(
    (settings.PACKAGE_NAME_GRAPPELLI, patterns("",
        ("^grappelli/", include("%s.urls" %
            settings.PACKAGE_NAME_GRAPPELLI)),
        ("^%s/admin/(?P<path>.*)$" % urlsplit(settings.ADMIN_MEDIA_PREFIX
            ).path.strip("/").split("/")[0], "django.views.static.serve",
            {'document_root': getattr(settings, "GRAPPELLI_MEDIA_PATH", "")}),
    )))

# Add patterns for optionally installed apps.
for (app, app_patterns) in OPTIONAL_APP_PATTERNS:
    if app in settings.INSTALLED_APPS:
        urlpatterns += app_patterns
