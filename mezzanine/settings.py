# Django settings for mezzanine project.

import os

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
TEMPLATE_DEBUG = True

ADMINS = (
    ('Patrick J. McNerthney', 'pat@mcnerthney.com'),
)

MANAGERS = ADMINS

if DEBUG:
    DATABASES = {
        'default': {
            "ENGINE": "sqlite3",
            "NAME": os.path.join(base_directory, "mezzanine.db"),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'postgresql_psycopg2',
            'NAME': 'mcnerthney',
            'USER': 'storm',
            'PASSWORD': 'storm',
            'HOST': 'localhost',
            'PORT': '',
        }
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Etc/UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(base_directory, MEDIA_URL.strip("/"))

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = "/admin/media/"

# Default e-mail address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = 'mezzanine@mcnerthney.com'

# E-mail address that error messages come from.
SERVER_EMAIL = 'mezzanine@mcnerthney.com'

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = '[Mezzanine] '

# Make this unique, and don't share it with anybody.
SECRET_KEY = "b6055148-2c50-4ee5-adda-fc38502b707c0862d0d0-95e2-42d4-b477-b9dc5d027e4d42452e0f-b3e7-4d10-b0ec-4872b8e6c888"

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "grappelli.context_processors.admin_template_path",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "mezzanine.core.template_loader.Loader",
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    #"django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    #"django.middleware.cache.UpdateCacheMiddleware",
    #"django.middleware.cache.FetchFromCacheMiddleware",
    "mezzanine.configuration.middleware.SettingsMiddleware",
    #"mezzanine.core.middleware.MobileTemplate",
    #"mezzanine.core.middleware.AdminLoginInterfaceSelector",
)

ROOT_URLCONF = 'mezzanine.urls'

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "mezzanine.core",
    "mezzanine.configuration",
    "mezzanine.pages",
    "mezzanine.blog",
    "mezzanine.forms",
    #"mezzanine.twitter",
    "mezzanine.staff",
    "grappelli",
    "filebrowser",
    "django.contrib.admin",
    "django.contrib.admindocs",
)

GRAPPELLI_ADMIN_TITLE = 'McNerthney'

FILEBROWSER_URL_FILEBROWSER_MEDIA = ADMIN_MEDIA_PREFIX + 'filebrowser/'
FILEBROWSER_DIRECTORY = ''
