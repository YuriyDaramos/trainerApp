from django.urls import path

from . import views

urlpatterns = [
    path("", views.trainers_page, name="trainers_page"),
    path("<int:trainer_id>/", views.specific_trainer_page, name="specific_trainer_page"),
    path("<int:trainer_id>/<int:service_id>/", views.specific_trainer_page_service, name="specific_trainer_page_service"),
    path("<int:trainer_id>/<int:service_id>/booking/", views.specific_trainer_page_service_booking, name="trainer_booking"),
]
