from django.urls import path

from . import views

urlpatterns = [
    path("", views.trainers, name="trainers_page"),
    path("<int:trainer_id>/", views.trainer_detail, name="specific_trainer_page"),
    path("<int:trainer_id>/service/", views.service_page, name="service_page"),
    path("<int:trainer_id>/<int:service_id>/booking/", views.book_service, name="book_service"),
]
