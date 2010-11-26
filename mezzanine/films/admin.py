
from copy import deepcopy
from django.contrib import admin
from mezzanine.core.admin import DynamicInlineAdmin
from mezzanine.films.models import Person, StaffPage, Member
from mezzanine.pages.admin import PageAdmin


class PersonAdmin(admin.ModelAdmin):
    pass

class MemberAdmin(DynamicInlineAdmin):
    model = Member

staff_page_fieldsets = deepcopy(PageAdmin.fieldsets)
staff_page_fieldsets[0][1]["fields"].append("summary")

class StaffPageAdmin(PageAdmin):
    inlines = (MemberAdmin,)
    fieldsets = staff_page_fieldsets


admin.site.register(Person, PersonAdmin)
admin.site.register(StaffPage, StaffPageAdmin)
