
from mezzanine.core.managers import DisplayableManager

class PageManager(DisplayableManager):

    def home(self, settings):
        try:
            return self.get(settings=settings, slug='')
        except self.model.DoesNotExist:
            return None
