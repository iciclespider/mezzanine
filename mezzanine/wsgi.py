
import _setup # Must be first
import django.core.handlers.wsgi
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'mezzanine.settings'
application = django.core.handlers.wsgi.WSGIHandler()
