from django.urls import path
from . import views


urlpatterns = [
    path("dates/", views.dates, name="dates"),
    path("scheduled-viewing/", views.scheduled_viewing, name="scheduled-viewing"),
    path("my-account/", views.my_account, name="my-account"),
    path("contact-us/", views.contact_us, name="contact-us"),
]
