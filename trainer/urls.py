from django.urls import path

from . import views

urlpatterns = [
    path("", views.trainers, name="trainers_page"),
    path("<int:trainer_id>/", views.trainer_detail, name="trainer_detail"),
    path("<int:trainer_id>/service/", views.service_page, name="service_page"),
    path("<int:trainer_id>/booking/<int:service_id>/", views.book_service, name="book_service"),
]
