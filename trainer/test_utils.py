import os
import django
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

os.environ['DJANGO_SETTINGS_MODULE'] = 'trainerApp.settings'
django.setup()

from trainer.utils import booking_time_discovery
import trainer
from booking.models import Booking


class TestBookingTimeDiscovery(unittest.TestCase):
    def setUp(self):
        # Фиктивные данные
        self.year = 2050
        self.month = 1
        self.day = 1
        self.trainer_id = 1
        self.service_id = 1
        self.date = datetime(self.year, self.month, self.day).date()

        # Мок расписания тренера
        self.schedule = [
            MagicMock(datetime_start=datetime(self.year, self.month, self.day, 10, 0),
                      datetime_end=datetime(self.year, self.month, self.day, 12, 0)),  # 10:00 - 12:00
            MagicMock(datetime_start=datetime(self.year, self.month, self.day, 13, 0),
                      datetime_end=datetime(self.year, self.month, self.day, 15, 0)),  # 13:00 - 15:00
        ]

        # Мок бронирований
        self.bookings = [
            MagicMock(datetime_start=datetime(self.year, self.month, self.day, 10, 0),
                      datetime_end=datetime(self.year, self.month, self.day, 10, 30), status=True),  # 10:00 - 10:30
            MagicMock(datetime_start=datetime(self.year, self.month, self.day, 13, 0),
                      datetime_end=datetime(self.year, self.month, self.day, 14, 0), status=True),  # 13:00 - 14:00
            MagicMock(datetime_start=datetime(self.year, self.month, self.day, 14, 30),
                      datetime_end=datetime(self.year, self.month, self.day, 15, 0), status=True),  # 14:30 - 15:00
        ]

        # Мок запросов к БД
        trainer.models.TrainerSchedule.objects.filter = MagicMock(return_value=self.schedule)
        trainer.models.Service.objects.get = MagicMock(return_value=None)
        Booking.objects.filter = MagicMock(return_value=self.bookings)

    def test_booking_time_discovery_15min_service(self):
        # Мок сервиса с длительностью 15 минут
        self.service = MagicMock(duration=timedelta(minutes=15))
        trainer.models.Service.objects.get.return_value = self.service

        # Вызов функции
        free_slots = booking_time_discovery(self.trainer_id, self.service_id, self.date)

        # Ожидаемые свободные слоты для сервиса в 15 минут
        expected_slots = [
            # 10:00-12:00
            (datetime(self.year, self.month, self.day, 10, 30), datetime(self.year, self.month, self.day, 10, 45)),  # 10:30 - 10:45
            (datetime(self.year, self.month, self.day, 10, 45), datetime(self.year, self.month, self.day, 11, 0)),  # 10:45 - 11:00
            (datetime(self.year, self.month, self.day, 11, 0), datetime(self.year, self.month, self.day, 11, 15)),  # 11:00 - 11:15
            (datetime(self.year, self.month, self.day, 11, 15), datetime(self.year, self.month, self.day, 11, 30)),  # 11:15 - 11:30
            (datetime(self.year, self.month, self.day, 11, 30), datetime(self.year, self.month, self.day, 11, 45)),  # 11:30 - 11:45
            (datetime(self.year, self.month, self.day, 11, 45), datetime(self.year, self.month, self.day, 12, 0)),  # 11:45 - 12:00

            # 13:00-15:00
            (datetime(self.year, self.month, self.day, 14, 0), datetime(self.year, self.month, self.day, 14, 15)),  # 14:00 - 14:15
            (datetime(self.year, self.month, self.day, 14, 15), datetime(self.year, self.month, self.day, 15, 00)),  # 14:15 - 15:00
        ]

        self.assertEqual(free_slots, expected_slots)

    def test_booking_time_discovery_45min_service(self):
        # Мок сервиса с длительностью 45 минут
        self.service = MagicMock(duration=timedelta(minutes=45))
        trainer.models.Service.objects.get.return_value = self.service

        # Вызов функции
        free_slots = booking_time_discovery(self.trainer_id, self.service_id, self.date)

        # Ожидаемые свободные слоты для сервиса в 45 минут
        expected_slots = [
            # 10:00-12:00
            (datetime(self.year, self.month, self.day, 10, 30), datetime(self.year, self.month, self.day, 11, 15)),  # 10:30 - 11:15
            (datetime(self.year, self.month, self.day, 10, 45), datetime(self.year, self.month, self.day, 11, 30)),  # 10:45 - 11:30
            (datetime(self.year, self.month, self.day, 11, 0), datetime(self.year, self.month, self.day, 11, 45)),  # 11:00 - 11:45
            (datetime(self.year, self.month, self.day, 11, 15), datetime(self.year, self.month, self.day, 12, 0)),  # 11:15 - 12:00
        ]

        self.assertEqual(free_slots, expected_slots)


if __name__ == "__main__":
    unittest.main()
