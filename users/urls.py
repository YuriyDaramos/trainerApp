from django.urls import path

from . import views

urlpatterns = [
    path("", views.user_page, name="user_page"),
    path("<int:user_id>/", views.specific_user_page, name="specific_user_page"),
]
