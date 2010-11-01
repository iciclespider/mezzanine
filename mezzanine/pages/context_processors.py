
from mezzanine.pages.models import ContentFragment

class Fragment(object):
    def __getitem__(self, key):
        try:
            fragment = ContentFragment.objects.get(name=key)
        except ContentFragment.DoesNotExist:
            raise KeyError('ContentFragment "%s" does not exist.' % key)
        return fragment.content

_fragment = {"fragment": Fragment()}

def content(request):
    return _fragment
