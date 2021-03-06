
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Model
from django.template import (Context, Node, TextNode, NodeList, FilterExpression,
    Template, TemplateSyntaxError)
from django.template.defaultfilters import truncatewords_html
from django.template.loader import get_template, Template
from django.template.loader_tags import BlockNode
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.simplejson import loads
from django.utils.text import capfirst
from mezzanine import template
from mezzanine.clevercss import convert as ccss_convert
from mezzanine.core.forms import get_edit_form
from mezzanine.utils.html import decode_entities
from mezzanine.utils.urls import admin_url
from mezzanine.utils.views import is_editable
from urllib import urlopen, urlencode
from uuid import uuid4
import os


register = template.Library()

@register.render_tag
def set_short_url_for(context, token):
    """
    Sets the ``short_url`` attribute of the given model using the bit.ly
    credentials if they have been specified and saves it.
    """
    obj = context[token.split_contents()[1]]
    request = context["request"]
    if getattr(obj, "short_url") is None:
        obj.short_url = request.build_absolute_uri(request.path)
        settings = context["request"].settings
        args = {
            "login": settings.BLOG_BITLY_USER,
            "apiKey": settings.BLOG_BITLY_KEY,
            "longUrl": obj.short_url,
        }
        if args["login"] and args["apiKey"]:
            url = "http://api.bit.ly/v3/shorten?%s" % urlencode(args)
            response = loads(urlopen(url).read())
            if response["status_code"] == 200:
                obj.short_url = response["data"]["url"]
                obj.save()
    return ""


@register.to_end_tag
def metablock(context, nodelist):
    """
    Remove HTML tags, entities and superfluous characters from meta blocks.
    """
    parsed = nodelist.render(context)
    parsed = " ".join(parsed.replace("\n", "").split()).replace(" ,", ",")
    return strip_tags(decode_entities(parsed))


@register.inclusion_tag("includes/pagination.html", takes_context=True)
def pagination_for(context, current_page):
    """
    Include the pagination template and data for persisting querystring in
    pagination links.
    """
    querystring = context["request"].GET.copy()
    if "page" in querystring:
        del querystring["page"]
    querystring = querystring.urlencode()
    return {"current_page": current_page, "querystring": querystring}


@register.simple_tag
def thumbnail(image_url, width, height):
    """
    Given the url to an image, resizes the image using the given width and 
    height on the first time it is requested, and returns the url to the new 
    resized image. if width or height are zero then original ratio is 
    maintained.
    """

    image_url = unicode(image_url)
    image_path = os.path.join(settings.MEDIA_ROOT, image_url)
    image_dir, image_name = os.path.split(image_path)
    thumb_name = "%s-%sx%s.jpg" % (os.path.splitext(image_name)[0], width, height)
    thumb_path = os.path.join(image_dir, thumb_name)
    thumb_url = "%s/%s" % (os.path.dirname(image_url), thumb_name)

    # abort if thumbnail exists, original image doesn't exist, invalid width or 
    # height are given, or PIL not installed
    if not image_url:
        return ""
    if os.path.exists(thumb_path):
        return thumb_url
    try:
        width = int(width)
        height = int(height)
    except ValueError:
        return image_url
    if not os.path.exists(image_path) or (width == 0 and height == 0):
        return image_url
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return image_url

    # open image, determine ratio if required and resize/crop/save
    image = Image.open(image_path)
    if width == 0:
        width = image.size[0] * height / image.size[1]
    elif height == 0:
        height = image.size[1] * width / image.size[0]
    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")
    try:
        image = ImageOps.fit(image, (width, height), Image.ANTIALIAS).save(
            thumb_path, "JPEG", quality=100)
    except:
        return image_url
    return thumb_url


@register.inclusion_tag("admin/includes/editable_loader.html", takes_context=True)
def editable_loader(context):
    """
    Set up the required JS/CSS for the in-line editing toolbar and controls.
    """
    t = get_template("admin/includes/editable_toolbar.html")
    context["REDIRECT_FIELD_NAME"] = REDIRECT_FIELD_NAME
    context["toolbar"] = t.render(Context(context))
    return context


@register.to_end_tag
def editable(context, nodelist, token):
    """
    Add the required HTML to the parsed content for in-line editing, such as
    the icon and edit form if the object is deemed to be editable - either it
    has an ``editable`` method which returns True, or the logged in user has
    change permissions for the model.
    """
    def parse_field(field):
        field = field.split(".")
        obj = context[field.pop(0)]
        attr = field.pop()
        while field:
            obj = getattr(obj, field.pop(0))
        return obj, attr

    fields = [parse_field(f) for f in token.split_contents()[1:]]
    if fields:
        fields = [f for f in fields if len(f) == 2 and f[0] is fields[0][0]]
    parsed = nodelist.render(context)
    if not parsed.strip():
        parsed = "".join([unicode(getattr(*field)) for field in fields])
    if fields:
        obj = fields[0][0]
        if isinstance(obj, Model) and is_editable(obj, context["request"]):
            field_names = ",".join([f[1] for f in fields])
            context["form"] = get_edit_form(obj, field_names)
            context["original"] = parsed
            context["uuid"] = uuid4()
            t = get_template("admin/includes/editable_form.html")
            return t.render(Context(context))
    return parsed


@register.simple_tag
def try_url(url_name):
    """
    Mimics Django's ``url`` template tag but fails silently. Used for urls 
    in admin templates as these urls won't resolve when admin tests are 
    running.
    """
    try:
        url = reverse(url_name)
    except NoReverseMatch:
        return ""
    return url


def admin_app_list(request):
    """
    Adopted from ``django.contrib.admin.sites.AdminSite.index``. Returns a 
    list of lists of models grouped and ordered according to 
    ``request.settings.ADMIN_MENU_ORDER``. Called from the 
    ``admin_dropdown_menu`` template tag as well as the ``app_list`` 
    dashboard widget.
    """
    app_dict = {}
    menu_order = [(x[0], list(x[1])) for x in request.settings.ADMIN_MENU_ORDER]
    found_items = set()
    for (model, model_admin) in admin.site._registry.items():
        opts = model._meta
        in_menu = not hasattr(model_admin, "in_menu") or model_admin.in_menu()
        if in_menu and request.user.has_module_perms(opts.app_label):
            perms = model_admin.get_model_perms(request)
            admin_url_name = ""
            if perms["change"]:
                admin_url_name = "changelist"
            elif perms["add"]:
                admin_url_name = "add"
            if admin_url_name:
                model_label = "%s.%s" % (opts.app_label, opts.object_name)
                for (name, items) in menu_order:
                    try:
                        index = list(items).index(model_label)
                    except ValueError:
                        pass
                    else:
                        found_items.add(model_label)
                        app_title = name
                        break
                else:
                    index = None
                    app_title = opts.app_label
                model_dict = {
                    "index": index,
                    "perms": model_admin.get_model_perms(request),
                    "name": capfirst(model._meta.verbose_name_plural),
                    "admin_url": admin_url(model, admin_url_name),
                }
                app_title = app_title.title()
                if app_title in app_dict:
                    app_dict[app_title]["models"].append(model_dict)
                else:
                    try:
                        titles = [x[0] for x in
                            request.settings.ADMIN_MENU_ORDER]
                        index = titles.index(app_title)
                    except ValueError:
                        index = None
                    app_dict[app_title] = {
                        "index": index,
                        "name": app_title,
                        "models": [model_dict],
                    }

    for (i, (name, items)) in enumerate(menu_order):
        for unfound_item in set(items) - found_items:
            if isinstance(unfound_item, (list, tuple)):
                item_name, item_url = unfound_item[0], try_url(unfound_item[1])
                if item_url:
                    if name not in app_dict:
                        app_dict[name] = {
                            "index": i,
                            "name": name,
                            "models": [],
                        }
                    app_dict[name]["models"].append({
                        "index": items.index(unfound_item),
                        "perms": {"custom": True},
                        "name": item_name,
                        "admin_url": item_url,
                    })

    app_list = app_dict.values()
    sort = lambda x: x["name"] if x["index"] is None else x["index"]
    for app in app_list:
        app["models"].sort(key=sort)
    app_list.sort(key=sort)
    return app_list


@register.inclusion_tag("admin/includes/dropdown_menu.html", takes_context=True)
def admin_dropdown_menu(context):
    """
    Renders the app list for the admin dropdown menu navigation.
    """
    context["dropdown_menu_app_list"] = admin_app_list(context["request"])
    return context


@register.inclusion_tag("admin/includes/app_list.html", takes_context=True)
def app_list(context):
    """
    Renders the app list for the admin dashboard widget.
    """
    context["dashboard_app_list"] = admin_app_list(context["request"])
    return context


@register.inclusion_tag("admin/includes/recent_actions.html", takes_context=True)
def recent_actions(context):
    """
    Renders the recent actions list for the admin dashboard widget.
    """
    return context


@register.render_tag
def dashboard_column(context, token):
    """
    Takes an index for retrieving the sequence of template tags from 
    ``request.settings.DASHBOARD_TAGS`` to render into the admin dashboard.
    """
    column_index = int(token.split_contents()[1])
    output = []
    for tag in context["request"].settings.DASHBOARD_TAGS[column_index]:
        try:
            t = Template("{%% load %s %%}{%% %s %%}" % tuple(tag.split(".")))
            output.append(t.render(Context(context)))
        except TemplateSyntaxError:
            pass
    return "".join(output)


@register.simple_context_tag
def render(context, *args):
    """
    Renders the arguments as a template themselves. This allows for treating
    text obtained from the model as template code.
      {% render page.content %}
    """
    if len(args) == 1:
        return Template(args[0], 'render').render(context)
    bits = []
    for arg in args:
        bits.append(Template(arg, 'render').render(context))
    return mark_safe(u''.join(bits))

@register.simple_context_tag
def rendersummary(context, *args):
    """
    Renders the arguments as a template themselves. This allows for treating
    text obtained from the model as template code.
      {% render page.content %}
    """
    if len(args) == 1:
        return Template(args[0], 'rendersummary').render(context)
    bits = []
    for arg in args:
        bits.append(Template(arg, 'rendersummary').render(context))
    summary = mark_safe(u''.join(bits))
    for end in ("</p>", "<br />", "<br/>", "</br>", "\n", ". "):
        if end in summary:
            summary = summary.split(end)[0] + end
    summary = truncatewords_html(summary, 100)
    return summary


BLOCK_MEDIAS = '__medias__'

class MediasNode(BlockNode):
    def render(self, context):
        context['medias'] = {}
        super(MediasNode, self).render(context)
        return u''

@register.tag
def medias(parser, token):
    bits = token.contents.split()
    if len(bits) != 1:
        raise TemplateSyntaxError("'%s' tag does not take any arguments" % bits[0])
    try:
        if BLOCK_MEDIAS in parser.__loaded_blocks:
            raise TemplateSyntaxError("'%s' tag appears more than once" % bits[0])
        parser.__loaded_blocks.append(BLOCK_MEDIAS)
    except AttributeError: # parser.__loaded_blocks isn't a list yet
        parser.__loaded_blocks = [BLOCK_MEDIAS]
    return MediasNode(BLOCK_MEDIAS, NodeList())

class MediaNode(Node):
    def __init__(self, type, nodelist):
        self.type = type
        self.nodelist = nodelist

    def render(self, context):
        if isinstance(self.type, FilterExpression):
            self.type = self.type.resolve(context)
        value = self.nodelist.render(context)
        medias = context['medias']
        values = medias.get(self.type)
        if values is None:
            medias[self.type] = [value]
        else:
            if value not in values:
                values.append(value)
        return u''

@register.tag
def media(parser, token):
    bits = token.split_contents()
    if bits[0] == 'media':
        if len(bits) != 2:
            raise TemplateSyntaxError("'media' takes one argument (type)")
        type = parser.compile_filter(bits[1])
    else:
        if len(bits) != 1:
            raise TemplateSyntaxError("'%s' does not take arguments" % bits[0])
        type = bits[0]
    nodelist = parser.parse(('end' + bits[0],))
    parser.delete_first_token()
    node = MediaNode(type, nodelist)
    try:
        block = parser.__medias_block
        block.nodelist.append(node)
        return TextNode('')
    except AttributeError:
        pass
    try:
        if BLOCK_MEDIAS in parser.__loaded_blocks:
            return node
        parser.__loaded_blocks.append(BLOCK_MEDIAS)
    except AttributeError:
        parser.__loaded_blocks = [BLOCK_MEDIAS]
    nodelist = NodeList()
    nodelist.contains_nontext = True
    nodelist.append(parser.create_variable_node(parser.compile_filter('block.super')))
    nodelist.append(node)
    block = BlockNode(BLOCK_MEDIAS, nodelist)
    parser.__medias_block = block
    return block

@register.to_end_tag
def ccss(context, nodelist):
    return mark_safe(ccss_convert(nodelist.render(context)))
