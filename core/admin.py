from django.contrib import admin
from .models import *

# Register your models here.


class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 1


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0


class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        "agent",
        "name",
        "price",
        "discount_price",
        "rent",
        "security_deposit",
        "bedrooms",
        "bathrooms",
        "meter",
        "available",
    ]
    list_filter = [
        "agent",
        "price",
        "discount_price",
        "rent",
        "bedrooms",
        "bathrooms",
        "meter",
        "available",
    ]
    inlines = (GalleryInline, ScheduleInline)
    list_editable = ("available",)
    list_per_page = 30


class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "sender",
        "receiver",
        "properties__name",
        "status",
    ]
    list_filter = [
        "sender",
        "receiver",
        "status",
    ]
    list_editable = ["status"]
    list_per_page = 30


admin.site.register(Property, PropertyAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Gallery)
admin.site.register(Category)
admin.site.register(InteriorFeatures)
admin.site.register(BuildingAmenities)
