
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import get_model
from django.http import (HttpResponse, Http404, HttpResponseNotFound,
    HttpResponseServerError)
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views import debug
from mezzanine.core.forms import get_edit_form
from mezzanine.core.models import Keyword, Displayable
from mezzanine.utils import is_editable, paginate
import sys


def admin_keywords_submit(request):
    """
    Adds any new given keywords from the custom keywords field in the admin and
    returns their IDs for use when saving a model with a keywords field.
    """
    ids = []
    for title in request.POST.get("text_keywords", "").split(","):
        title = "".join([c for c in title if c.isalnum() or c == "-"]).lower()
        if title:
            keyword, created = Keyword.objects.get_or_create(title=title)
            ids.append(str(keyword.id))
    return HttpResponse(",".join(set(ids)))
admin_keywords_submit = staff_member_required(admin_keywords_submit)


def search(request, template="search_results.html"):
    """
    Display search results.
    """
    query = request.GET.get("q", "")
    results = Displayable.objects.search(request.settings, query)
    results = paginate(results, request.GET.get("page", 1),
        request.settings.SEARCH_PER_PAGE, request.settings.SEARCH_MAX_PAGING_LINKS)
    context = {"query": query, "results": results}
    return render_to_response(template, context, RequestContext(request))


def edit(request):
    """
    Process the inline editing form.
    """
    model = get_model(request.POST["app"], request.POST["model"])
    obj = model.objects.get(id=request.POST["id"])
    form = get_edit_form(obj, request.POST["fields"], data=request.POST,
                        files=request.FILES)
    if not is_editable(obj, request):
        response = _("Permission denied")
    elif form.is_valid():
        form.save()
        response = ""
    else:
        response = form.errors.values()[0][0]
    return HttpResponse(unicode(response))

def force404(request, url=None):
    raise Http404

def force500(request, url=None):
    raise Exception('Forced 500.')

def handler404(request):
    if request.settings.DEBUG:
        return debug.technical_404_response(request, sys.exc_info()[1])
    template = loader.get_template(request.settings.TEMPLATE_404)
    return HttpResponseNotFound(template.render(RequestContext(request)))

def handler500(request):
    if request.settings.DEBUG:
        return debug.technical_500_response(request, *sys.exc_info())
    template = loader.get_template(request.settings.TEMPLATE_500)
    return HttpResponseServerError(template.render(RequestContext(request)))

