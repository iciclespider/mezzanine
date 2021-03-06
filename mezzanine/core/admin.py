
from django import forms
from django.contrib import admin
from django.db.models import AutoField
from django.http import HttpResponseRedirect
from mezzanine.core.forms import DynamicInlineAdminForm
from mezzanine.core.models import Orderable, Template
from mezzanine.utils.urls import content_media_urls, admin_url


# Build the list of admin JS file for ``Displayable`` models.
displayable_js = ["js/jquery-1.4.2.min.js",
    "js/keywords_field.js"]
displayable_js = content_media_urls(*displayable_js)
#displayable_js.append("%s/jscripts/tiny_mce/tiny_mce_src.js" % global_settings.TINYMCE_URL)
#displayable_js.extend(content_media_urls("js/tinymce_setup.js"))


class DisplayableAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        #if len(args) > 0:
        #    if not args[0].get('initial') and request.settings.exists:
        #        POST = args[0].copy()
        #        POST['settings'] = request.settings.id
        #        args = [POST]
        #        args.extend(args[1:])
        #else:
        #    initial = kwargs.get('initial')
        #    if initial is not None and not initial.get('settings') and request.settings.exists:
        #        initial['settings'] = request.settings
        super(DisplayableAdminForm, self).__init__(*args, **kwargs)

    #def _get_validation_exclusions(self):
    #    exclusions = super(DisplayableAdminForm, self)._get_validation_exclusions()
    #    # prevent the check for settings, slug unique together by the form.
    #    exclusions.append('slug')
    #    return exclusions

class DisplayableAdmin(admin.ModelAdmin):
    """
    Admin class for subclasses of the abstract ``Displayable`` model.
    """

    class Media:
        js = displayable_js

    list_display = ("title", "status", "admin_link")
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status",)
    search_fields = ("title", "content",)
    date_hierarchy = "publish_date"
    radio_fields = {"status": admin.HORIZONTAL}
    fieldsets = [
        (None, {"fields": ["title",
                          ]
               },
        ),
        ("Meta data", {"fields": ["status",
                                  ("publish_date", "expiry_date"),
                                  "slug",
                                  "description",
                                  "keywords",
                                 ],
                          "classes": ("collapse", "closed")
                         },
        ),
    ]
    #form = DisplayableAdminForm

    def save_form(self, request, form, change):
        """
        Store the keywords as a single string into the ``_keywords`` field
        for convenient access when searching.
        """
        obj = form.save(commit=True)
        obj.set_searchable_keywords()
        return super(DisplayableAdmin, self).save_form(request, form, change)


class DynamicInlineAdmin(admin.TabularInline):
    """
    Admin inline that uses JS to inject an "Add another" link when when 
    clicked, dynamically reveals another fieldset. Also handles adding the 
    ``_order`` field and its widget for models that subclass ``Orderable``.
    """

    form = DynamicInlineAdminForm
    extra = 0
    template = "admin/includes/dynamic_inline.html"

    def __init__(self, *args, **kwargs):
        super(DynamicInlineAdmin, self).__init__(*args, **kwargs)
        if issubclass(self.model, Orderable):
            fields = self.fields
            if not fields:
                fields = self.model._meta.fields
                exclude = self.exclude or []
                fields = [f.name for f in fields if f.editable and
                    f.name not in exclude and not isinstance(f, AutoField)]
            if "_order" in fields:
                del fields[fields.index("_order")]
                fields.append("_order")
            self.fields = fields


class OwnableAdmin(admin.ModelAdmin):
    """
    Admin class for models that subclass the abstract ``Ownable`` model.
    Handles limiting the change list to objects owned by the logged in user,
    as well as setting the owner of newly created objects to the logged in
    user.
    """

    def save_form(self, request, form, change):
        """
        Set the object's owner as the logged in user.
        """
        obj = form.save(commit=False)
        if obj.user_id is None:
            obj.user = request.user
        return super(OwnableAdmin, self).save_form(request, form, change)

    def queryset(self, request):
        """
        Filter the change list by currently logged in user if not a superuser.
        """
        qs = super(OwnableAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user__id=request.user.id)


class SingletonAdmin(admin.ModelAdmin):
    """
    Admin class for models that should only contain a single instance in the 
    database. Redirect all views to the change view when the instance exists, 
    and to the add view when it doesn't.
    """

    def add_view(self, *args, **kwargs):
        """
        Redirect to the change view if the singlton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            return super(SingletonAdmin, self).add_view(*args, **kwargs)
        else:
            change_url = admin_url(self.model, "change", singleton.id)
            return HttpResponseRedirect(change_url)

    def changelist_view(self, *args, **kwargs):
        """
        Redirect to the add view if no records exist or the change view if 
        the singlton instance exists.
        """
        try:
            singleton = self.model.objects.get()
        except self.model.MultipleObjectsReturned:
            return super(SingletonAdmin, self).changelist_view(*args, **kwargs)
        except self.model.DoesNotExist:
            add_url = admin_url(self.model, "add")
            return HttpResponseRedirect(add_url)
        else:
            change_url = admin_url(self.model, "change", singleton.id)
            return HttpResponseRedirect(change_url)

    def change_view(self, request, object_id, extra_context=None):
        """
        If only the singleton instance exists, pass True for ``singleton`` 
        into the template which will use CSS to hide relevant buttons.
        """
        if extra_context is None:
            extra_context = {}
        try:
            self.model.objects.get()
        except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
            pass
        else:
            extra_context["singleton"] = True
        return super(SingletonAdmin, self).change_view(request, object_id,
                                                        extra_context)


class TemplateAdmin(admin.ModelAdmin):
    """
    Admin class for Template model.
    """
    list_filter = ('directory', 'name', 'extension')
    search_fields = ('content',)
    fields = ('directory', 'name', 'extension', 'content')

admin.site.register(Template, TemplateAdmin)
