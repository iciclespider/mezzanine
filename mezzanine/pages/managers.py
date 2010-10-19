
from mezzanine.core.managers import DisplayableManager


class PageManager(DisplayableManager):
    """
    Manager for the ``page`` model.
    """
    def get_home_page(self, request):
        host = request.META["HTTP_HOST"]
        domain = host.split(':')[0]
        return self.get(sites__site__domain=domain)
