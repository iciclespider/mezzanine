
import _setup # Must be first
import django.core.handlers.wsgi
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'mezzanine.settings'
sys.stdout = sys.stderr
application = django.core.handlers.wsgi.WSGIHandler()
