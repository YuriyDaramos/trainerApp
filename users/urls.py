from django.urls import path

from . import views

urlpatterns = [
    path("", views.users, name="users_page"),
    path("<int:user_id>/", views.user_details, name="user_details"),
    path("user/<int:user_id>/rate/", views.add_or_update_rating, name="add_or_update_rating"),
]
