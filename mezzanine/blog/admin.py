
from copy import deepcopy
from django.contrib import admin
from mezzanine.blog.models import Blog, Post, Category, Comment
from mezzanine.configuration import global_settings
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin
from mezzanine.pages.admin import PageAdmin

blog_fieldsets = deepcopy(PageAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].extend(("summary", ("_posts_per_page", "_max_paging_links")))
blog_fieldsets[1][1]["fields"].extend(("post_style", "post_template"))

post_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
post_fieldsets[0][1]["fields"].insert(0, ('blog', 'category'))
post_fieldsets[0][1]["fields"].append("content")
post_radio_fields = deepcopy(DisplayableAdmin.radio_fields)
post_radio_fields["category"] = admin.HORIZONTAL


class BlogAdmin(PageAdmin):
    fieldsets = blog_fieldsets

class PostAdmin(DisplayableAdmin, OwnableAdmin):
    """
    Admin class for blog posts.
    """

    fieldsets = post_fieldsets
    list_display = ("title", "user", "status", "admin_link")
    radio_fields = post_radio_fields

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)


class CategoryAdmin(admin.ModelAdmin):
    """
    Admin class for blog categories. Hides itself from the admin menu
    unless explicitly specified.
    """

    fieldsets = ((None, {"fields": ("title",)}),)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in global_settings.ADMIN_MENU_ORDER:
            if "blog.BlogCategory" in items:
                return True
        return False


class CommentAdmin(admin.ModelAdmin):
    """
    Admin class for blog comments.
    """

    list_display = ("avatar_link", "intro", "time_created", "approved",
        "post", "admin_link")
    list_display_links = ("intro", "time_created")
    list_editable = ("approved",)
    list_filter = ("post", "approved", "name")
    search_fields = ("name", "email", "body")
    date_hierarchy = "time_created"
    ordering = ("-time_created",)
    fieldsets = (
        (None, {"fields": (("name", "email", "website"), "body",
            ("ip_address", "approved"), ("post", "replied_to"))}),
    )

admin.site.register(Blog, BlogAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Comment, CommentAdmin)
