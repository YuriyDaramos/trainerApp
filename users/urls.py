from django.urls import path

from . import views

urlpatterns = [
    path("", views.users, name="users_page"),
    path("<int:user_id>/", views.user_details, name="user_details"),
]
