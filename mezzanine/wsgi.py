
import _setup # Must be first
import django.core.handlers.wsgi
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'storm.settings'
application = django.core.handlers.wsgi.WSGIHandler()
