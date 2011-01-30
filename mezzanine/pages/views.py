
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from mezzanine.pages.models import Page


def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """
    for i, page in enumerate(request.POST.get("ordering", "").split(",")):
        Page.objects.filter(id=page.split("_")[-1]).update(_order=i)
    return HttpResponse("ok")
admin_page_ordering = staff_member_required(admin_page_ordering)

def page(request, url):
    if not request.settings.exists or not request.settings.homepage:
        return HttpResponse(request.settings.domain)
    return request.settings.homepage.response(request, url)
