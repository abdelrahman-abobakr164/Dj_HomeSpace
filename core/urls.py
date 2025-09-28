from django.urls import path
from .views import *
from .api import *


urlpatterns = [
    path("", index, name="index"),
    path("properties/", properties, name="properties"),
    path("services/", services, name="services"),
    path("privacy-policy/", privacy, name="privacy"),
    path("terms-of-Service/", terms, name="terms"),
    path("<str:username>/Add-Property/", add_property, name="add-property"),
    path("contact/<uuid:id>/", contact_agent, name="contact-agent"),
    path("update/<uuid:id>/", property_update, name="property_update"),
    path("delete/<uuid:id>/", property_delete, name="property_delete"),
    path("property/<uuid:id>/", property_detail, name="property"),
    path("service/<str:slug>/", service_detail, name="service"),
    # API
    path("rest-property-list/", PropertyList.as_view(), name="api_property_list"),
    path(
        "rest-property-detail/<uuid:id>/",
        PropertyDetail.as_view(),
        name="api_property_detail",
    ),
]
