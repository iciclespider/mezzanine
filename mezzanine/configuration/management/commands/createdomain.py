
from django import conf
from django.contrib.sites.models import Site
from django.core.management.base import LabelCommand, CommandError
from mezzanine.configuration.models import Settings, SiteSettings

class Command(LabelCommand):
    args = '<domain domain ...>'
    help = 'Create the domains.'

    def handle_label(self, domain, **options):
        try:
            site = Site.objects.get(domain=domain)
            return 'Domain %s already exists' % domain
        except Site.DoesNotExist:
            pass
        try:
            site = Site.objects.get(id=conf.settings.SITE_ID)
            if site.domain != 'example.com':
                site = Site()
        except Site.DoesNotExist:
            site = Site(id=conf.settings.SITE_ID)
        site.domain = domain
        site.name = domain
        site.save()
        try:
            settings = Settings.objects.get(name=domain)
        except:
            settings = Settings.objects.create(name=domain)
        SiteSettings.objects.create(site=site, settings=settings)
