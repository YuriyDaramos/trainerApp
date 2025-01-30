from datetime import timedelta, datetime
from django.urls import reverse

from django.test import TestCase, Client

# Create your tests here.
from django.contrib.auth.models import User, Group

import trainer.models
from booking.models import Booking


class TrainerTest(TestCase):
    def setUp(self):
        Group.objects.filter(name__in=["User", "Trainer"]).delete()

        self.first_name = "John"
        self.last_name = "Doe"
        self.password = "1111"
        self.default_user = User.objects.create_user(username="user",
                                                     email="user@email.com",
                                                     password=self.password,
                                                     first_name=self.first_name,
                                                     last_name=self.last_name)
        self.trainer_user = User.objects.create_user(username="trainer",
                                                     email="trainer@email.com",
                                                     password=self.password,
                                                     first_name=self.first_name,
                                                     last_name=self.last_name)
        self.default_user.groups.create(name="User")
        self.trainer_user.groups.create(name="Trainer")

        self.category = trainer.models.Category.objects.create(name="Fitness")

        self.service = trainer.models.Service(level=1,
                                              duration=timedelta(minutes=60),
                                              price=99,
                                              category=self.category,
                                              trainer=self.trainer_user)
        self.service.save()

        self.schedule_datetime_start = datetime(2025, 1, 1, 10, 0)
        self.schedule_datetime_end = datetime(2025, 1, 1, 20, 00)
        self.booking_date_start = "2025-01-01"
        self.booking_time = "10:00-11:00"

        self.client = Client()

    def test_list_of_trainers(self):
        url = reverse("trainer:trainers_page")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_trainer_service_page(self):
        url = reverse("trainer:trainer_detail", kwargs={"trainer_id": self.trainer_user.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_service(self):
        url = reverse("trainer:edit_trainer_service", kwargs={"trainer_id": self.trainer_user.id,
                                                              "service_id": self.service.id})
        post_data = {"service_id": str(self.service.id),
                     "category": self.category.id,
                     "duration": "02:00:00",
                     "price": 150,
                     "level": 2,
                     "delete": False}

        self.client.login(username="trainer", password=self.password)

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.service.refresh_from_db()
        self.assertEqual(self.service.duration, timedelta(hours=2))
        self.assertEqual(self.service.price, 150)
        self.assertEqual(self.service.level, 2)

        # if "delete"
        post_data["delete"] = True

        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(trainer.models.Service.objects.filter(id=self.service.id).exists())

    def test_add_service(self):
        url = reverse("trainer:add_trainer_service", kwargs={"trainer_id": self.trainer_user.id})
        post_data = {"level": "1",
                     "duration": "60",
                     "price": "99",
                     "category": str(self.category.id)}

        self.client.login(username="trainer", password=self.password)

        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            trainer.models.Service.objects.filter(trainer=self.trainer_user, category=self.category).exists())

        service = trainer.models.Service.objects.filter(trainer=self.trainer_user, category=self.category).first()
        self.assertEqual(service.level, 1)
        self.assertEqual(service.duration, timedelta(minutes=60))
        self.assertEqual(service.price, 99)

    def test_add_working_hours(self):
        url = reverse("trainer:set_working_hours", kwargs={"trainer_id": self.trainer_user.id})

        post_data = {"datetime_start": "2025-01-01T10:00",
                     "datetime_end": "2025-01-01T20:00"}

        self.client.login(username="trainer", password=self.password)
        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(trainer.models.TrainerSchedule.objects.filter(trainer=self.trainer_user).exists())

        schedule = trainer.models.TrainerSchedule.objects.get(trainer=self.trainer_user)
        self.assertEqual(schedule.datetime_start.strftime("%Y-%m-%dT%H:%M"), post_data["datetime_start"])
        self.assertEqual(schedule.datetime_end.strftime("%Y-%m-%dT%H:%M"), post_data["datetime_end"])

    def test_get_booking_page(self):
        self.trainer_schedule = trainer.models.TrainerSchedule.objects.create(trainer=self.trainer_user,
                                                                              datetime_start=self.schedule_datetime_start,
                                                                              datetime_end=self.schedule_datetime_end)

        url = reverse("trainer:book_service", kwargs={"trainer_id": self.trainer_user.id,
                                                      "service_id": self.service.id})

        # if User
        self.client.login(username="user", password=self.password)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # if Trainer
        self.client.login(username="trainer", password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_book_service(self):
        post_data = {"date": self.booking_date_start,
                     "booking_time": self.booking_time}

        url = reverse("trainer:book_service", kwargs={"trainer_id": self.trainer_user.id,
                                                      "service_id": self.service.id})

        # if User
        self.client.login(username="user", password=self.password)

        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.filter(trainer_id=self.trainer_user.id).exists())

        # if Trainer
        self.client.login(username="trainer", password=self.password)

        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 403)
