from django.urls import path

from . import views

urlpatterns = [
    path("<int:booking_id>/", views.booking_page, name="booking_page"),
    path("<int:booking_id>/accept/", views.booking_accept_page, name="booking_accept_page"),
    path("<int:booking_id>/cancel/", views.booking_cancel_page, name="booking_cancel_page"),
]
