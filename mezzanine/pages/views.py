
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.utils.http import urlquote
from mezzanine.pages import page_processors
from mezzanine.pages.models import Page


page_processors.autodiscover()


def admin_page_ordering(request):
    """
    Updates the ordering of pages via AJAX from within the admin.
    """
    for i, page in enumerate(request.POST.get("ordering", "").split(",")):
        Page.objects.filter(id=page.split("_")[-1]).update(_order=i)
    return HttpResponse("ok")
admin_page_ordering = staff_member_required(admin_page_ordering)


def home(request):
    if not request.settings.exists or not request.settings.homepage:
        return _handle_no_domain(request)
    return _handle_page(request, request.settings.homepage)

def page(request, slug):
    if not request.settings.exists:
        return _handle_no_domain(request)
    page = get_object_or_404(Page.objects.published(request.user), settings=request.settings, slug=slug)
    return _handle_page(request, page)

def _handle_no_domain(request):
    return HttpResponse(request.settings.domain)

def _handle_page(request, page):
    """
    Display content for a page. First check for any matching page processors
    and handle them. Secondly, build the list of template names to choose
    from given the slug and type of page being viewed.
    """
    if page.login_required and not request.user.is_authenticated():
        return redirect("%s?%s=%s" % (settings.LOGIN_URL, REDIRECT_FIELD_NAME,
            urlquote(request.get_full_path())))
    context = {"page": page.instance}
    for processor in page_processors.processors[page.content_model]:
        response = processor(request, page)
        if response:
            if isinstance(response, HttpResponse):
                return response
            if not isinstance(response, dict):
                raise ValueError("The page processor %s.%s returned %s but "
                    "must return HttpResponse or dict." % (
                    processor.__module__, processor.__name__, type(response)))
            context.update(response)
    return HttpResponse(page.get_template().render(RequestContext(request, context)))
