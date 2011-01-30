
from collections import defaultdict
from django.db.models import get_model, get_models
from django.template import TemplateSyntaxError, loader
from mezzanine import template
from mezzanine.pages.models import Page
from mezzanine.utils.urls import admin_url

register = template.Library()


def _page_menu(context, parent_page, admin=False):
    """
    Return a list of child pages for the given parent, storing all
    pages in a dict in the context when first called using parents as keys
    for retrieval on subsequent recursive calls from the menu template.
    """
    if "menu_pages" not in context:
        if admin:
            user = None
            slug = None
            home = None
        else:
            try:
                user = context["request"].user
            except KeyError:
                user = None
            try:
                slug = context["request"].path.strip("/")
            except KeyError:
                slug = ""
            home = Page.objects.home(context["request"].settings)
        pages = {}
        menu_pages = defaultdict(list)
        selected_page = None
        for page in Page.objects.published(for_user=user).order_by("_order"):
            setattr(page, "selected", False)
            setattr(page, "html_id", page.slug.replace("/", "-"))
            setattr(page, "primary", home and page.parent_id == home.id)
            setattr(page, "branch_level", 0)
            pages[page.id] = page
            menu_pages[page.parent_id].append(page)
            if home and page.id == home.id:
                context["home_page"] = page
                if not admin:
                    setattr(page, "branch_level", -1)
            if page.slug == slug:
                selected_page = page
        context["menu_pages"] = menu_pages
        while selected_page:
            selected_page.selected = True
            selected_page = pages.get(selected_page.parent_id, None)
    # ``branch_level`` must be stored against each page so that the 
    # calculation of it is correctly applied. This looks weird but if we do 
    # the ``branch_level`` as a separate arg to the template tag with the 
    # addition performed on it, the addition occurs each time the template 
    # tag is called rather than once per level.
    if not parent_page and not admin:
        parent_page = context["home_page"]
    if parent_page:
        branch_level = parent_page.branch_level + 1
        page_branch = context["menu_pages"][parent_page.id]
        for page in page_branch:
            page.branch_level = branch_level
    else:
        branch_level = 0
        page_branch = context["menu_pages"][None]
    context["branch_level"] = branch_level
    context["page_branch"] = page_branch
    return context


@register.inclusion_tag("pages/includes/tree_menu.html", takes_context=True)
def tree_menu(context, parent_page=None):
    """
    Tree menu that renders all pages in the navigation hierarchically.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("pages/includes/tree_menu_footer.html", takes_context=True)
def tree_menu_footer(context, parent_page=None):
    """
    Tree menu that renders all pages in the footer hierarchically.
    """
    return _page_menu(context, parent_page)


@register.simple_context_tag
def primary_menu(context, parent_page=None):
    """
    Page menu that only renders the primary top-level pages.
    """
    _page_menu(context, parent_page)
    return loader.render_to_string(context['request'].settings.TEMPLATE_PRIMARY_MENU, context)


@register.inclusion_tag("pages/includes/footer_menu.html", takes_context=True)
def footer_menu(context, parent_page=None):
    """
    Page menu that only renders the footer pages.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("pages/includes/breadcrumb_menu.html",
    takes_context=True)
def breadcrumb_menu(context, parent_page=None):
    """
    Page menu that only renders the pages that are parents of the current 
    page, as well as the current page itself.
    """
    return _page_menu(context, parent_page)


@register.inclusion_tag("admin/includes/tree_menu.html", takes_context=True)
def tree_menu_admin(context, parent_page=None):
    """
    Admin tree menu for managing pages.
    """
    return _page_menu(context, parent_page, True)


@register.as_tag
def models_for_pages(*args):
    """
    Create a select list containing each of the models that subclass the
    ``Page`` model.
    """
    page_models = []
    for model in get_models():
        if model is not Page and issubclass(model, Page):
            setattr(model, "name", model._meta.verbose_name)
            setattr(model, "add_url", admin_url(model, "add"))
            page_models.append(model)
    return page_models


@register.filter
def is_page_content_model(admin_model_dict):
    """
    Returns True if the model in the given admin dict is a subclass of the
    ``Page`` model.
    """
    args = admin_model_dict["admin_url"].strip("/").split("/")
    if len(args) == 2:
        model = get_model(*args)
        return model is not Page and issubclass(model, Page)
    return False

@register.to_end_tag
def page(context, nodelist, token, parser):
    """
    Allows a Page to be embedded in a template.
      {% page 'about' %}
        {{ page.title }}
      {% endpage %}
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument (slug)" % bits[0])
    slug = parser.compile_filter(bits[1]).resolve(context)
    try:
        page = Page.objects.get(slug=slug)
    except Page.DoesNotExist:
        raise TemplateSyntaxError("The Page slug '%s' does not exist." % slug)
    context['page'] = page
    return nodelist.render(context)
