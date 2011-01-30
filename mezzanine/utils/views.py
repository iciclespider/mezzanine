
from datetime import datetime, timedelta

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.template import Context

def is_editable(obj, request):
    """
    Returns ``True`` if the object is editable for the request. First check 
    for a custom ``editable`` handler on the object, otherwise use the logged
    in user and check change permissions for the object's model.
    """
    if hasattr(obj, "is_editable"):
        return obj.is_editable(request)
    else:
        perm = obj._meta.app_label + "." + obj._meta.get_change_permission()
        return request.user.is_authenticated() and request.user.has_perm(perm)


def paginate(objects, request, per_page, max_paging_links):
    """
    Return a paginated page for the given objects, giving it a custom
    ``visible_page_range`` attribute calculated from ``max_paging_links``.
    """
    querystring = request.GET.copy()
    page_num = querystring.pop("page", ["1"])[0]
    paginator = Paginator(list(objects), per_page)
    try:
        page_num = int(page_num)
    except ValueError:
        page_num = 1
    try:
        objects = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
    page_range = objects.paginator.page_range
    if len(page_range) > max_paging_links:
        start = min(objects.paginator.num_pages - max_paging_links,
            max(0, objects.number - (max_paging_links / 2) - 1))
        page_range = page_range[start:start + max_paging_links]
    objects.visible_page_range = page_range
    objects.querystring = querystring.urlencode()
    return objects


def set_cookie(response, name, value, expiry_seconds):
    """
    Set cookie wrapper that allows number of seconds to be given as the 
    expiry time, and ensures values are correctly encoded.
    """
    expires = datetime.strftime(datetime.utcnow() +
                                timedelta(seconds=expiry_seconds),
                                "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(name, value.encode("utf-8"), expires=expires)
