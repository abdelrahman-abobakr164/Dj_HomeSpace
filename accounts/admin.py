from django.contrib import admin
from .models import *

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "phone",
        "is_active",
        "is_staff",
        "is_superuser",
        "is_admin",
    ]
    list_display_links = ["email","username" ]


class ContactAdmin(admin.ModelAdmin):
    list_display = ["email"]
    list_display_links = ["email"]


admin.site.register(User, UserAdmin)
admin.site.register(Contact)
