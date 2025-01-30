from django.urls import path

from . import views

urlpatterns = [
    path("", views.trainers, name="trainers_page"),
    path("<int:trainer_id>/", views.trainer_detail, name="trainer_detail"),
    path("<int:trainer_id>/set_desc/", views.set_trainer_description, name="set_trainer_description"),
    path("<int:trainer_id>/set_schedule/", views.set_working_hours, name="set_working_hours"),
    path("<int:trainer_id>/service/edit/<int:service_id>/", views.edit_trainer_service, name="edit_trainer_service"),
    path("<int:trainer_id>/service/add/", views.add_trainer_service, name="add_trainer_service"),
    path("<int:trainer_id>/booking/<int:service_id>/", views.book_service, name="book_service"),
]
