
from django.http import Http404
from mezzanine.configuration.models import Settings

class LazySettings(object):
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_settings'):
            host = request.META["HTTP_HOST"]
            domain = host.split(':')[0]
            try:
                request._cached_settings = Settings.objects.get(sites__site__domain=domain)
                request._cached_settings.exists = True
            except Settings.DoesNotExist:
                request._cached_settings = Settings()
                request._cached_settings.exists = False
            request._cached_settings.domain = domain
        return request._cached_settings


class SettingsMiddleware(object):
    def process_request(self, request):
        request.__class__.settings = LazySettings()
        return None
