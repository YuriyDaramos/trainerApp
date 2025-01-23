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
        self.trainer_id = 1
        self.service_id = 1
        self.date = datetime(2025, 1, 23).date()

        # Мок расписания тренера
        self.schedule = [
            MagicMock(datetime_start=datetime(2025, 1, 23, 10, 0),
                      datetime_end=datetime(2025, 1, 23, 12, 0)),
                      # 10:00 - 12:00
            MagicMock(datetime_start=datetime(2025, 1, 23, 13, 0),
                      datetime_end=datetime(2025, 1, 23, 17, 0)),
                      # 13:00 - 17:00
        ]

        # Мок бронирований
        self.bookings = [
            MagicMock(datetime_start=datetime(2025, 1, 23, 10, 00),
                      datetime_end=datetime(2025, 1, 23, 10, 30), status=True),
                      # 10:00 - 10:30
            MagicMock(datetime_start=datetime(2025, 1, 23, 13, 0),
                      datetime_end=datetime(2025, 1, 23, 14, 0), status=True),
                      # 13:00 - 14:00
            MagicMock(datetime_start=datetime(2025, 1, 23, 15, 30),
                      datetime_end=datetime(2025, 1, 23, 16, 0), status=True),
                      # 15:30 - 16:00
        ]

        # Мок запросов к БД
        trainer.models.TrainerSchedule.objects.filter = MagicMock(return_value=self.schedule)
        trainer.models.Service.objects.get = MagicMock(return_value=None)  # Подменяется в каждом тесте
        Booking.objects.filter = MagicMock(return_value=self.bookings)

    def test_booking_time_discovery_15min_service(self):
        # Мок сервиса с длительностью 15 минут
        self.service = MagicMock(duration=timedelta(minutes=15))
        trainer.models.Service.objects.get.return_value = self.service

        # Вызов функции
        free_slots = booking_time_discovery(self.trainer_id, self.service_id, self.date)

        # Ожидаемые свободные слоты
        expected_slots = [
            # 10:00-12:00
            (datetime(2025, 1, 23, 10, 30), datetime(2025, 1, 23, 10, 45)),  # 10:30 - 10:45
            (datetime(2025, 1, 23, 10, 45), datetime(2025, 1, 23, 11, 0)),  # 10:45 - 11:00
            (datetime(2025, 1, 23, 11, 0), datetime(2025, 1, 23, 11, 15)),  # 11:00 - 11:15
            (datetime(2025, 1, 23, 11, 15), datetime(2025, 1, 23, 11, 30)),  # 11:15 - 11:30
            (datetime(2025, 1, 23, 11, 30), datetime(2025, 1, 23, 11, 45)),  # 11:30 - 11:45
            (datetime(2025, 1, 23, 11, 45), datetime(2025, 1, 23, 12, 0)),  # 11:45 - 12:00

            # 13:00-17:00
            (datetime(2025, 1, 23, 14, 0), datetime(2025, 1, 23, 14, 15)),  # 14:00 - 14:15
            (datetime(2025, 1, 23, 14, 15), datetime(2025, 1, 23, 14, 30)),  # 14:15 - 14:30
            (datetime(2025, 1, 23, 14, 30), datetime(2025, 1, 23, 14, 45)),  # 14:30 - 14:45
            (datetime(2025, 1, 23, 14, 45), datetime(2025, 1, 23, 15, 0)),  # 14:45 - 15:00
            (datetime(2025, 1, 23, 15, 0), datetime(2025, 1, 23, 15, 15)),  # 15:00 - 15:15
            (datetime(2025, 1, 23, 15, 15), datetime(2025, 1, 23, 15, 30)),  # 15:15 - 15:30
            (datetime(2025, 1, 23, 16, 0), datetime(2025, 1, 23, 16, 15)),  # 16:00 - 16:15
            (datetime(2025, 1, 23, 16, 15), datetime(2025, 1, 23, 16, 30)),  # 16:15 - 16:30
            (datetime(2025, 1, 23, 16, 30), datetime(2025, 1, 23, 16, 45)),  # 16:30 - 16:45
            (datetime(2025, 1, 23, 16, 45), datetime(2025, 1, 23, 17, 0)),  # 16:45 - 17:00
        ]

        self.assertEqual(free_slots, expected_slots)

    def test_booking_time_discovery_45min_service(self):
        # Мок сервиса с длительностью 45 минут
        self.service = MagicMock(duration=timedelta(minutes=45))
        trainer.models.Service.objects.get.return_value = self.service

        # Вызов функции
        free_slots = booking_time_discovery(self.trainer_id, self.service_id, self.date)

        # Ожидаемые свободные слоты
        expected_slots = [
            # 10:00-12:00
            (datetime(2025, 1, 23, 10, 30), datetime(2025, 1, 23, 11, 15)),  # 10:30 - 11:15
            (datetime(2025, 1, 23, 10, 45), datetime(2025, 1, 23, 11, 30)),  # 10:45 - 11:30
            (datetime(2025, 1, 23, 11, 0), datetime(2025, 1, 23, 11, 45)),  # 11:00 - 11:45
            (datetime(2025, 1, 23, 11, 15), datetime(2025, 1, 23, 12, 0)),  # 11:15 - 12:00

            # 13:00-17:00
            (datetime(2025, 1, 23, 14, 0), datetime(2025, 1, 23, 14, 45)),  # 14:00 - 14:45
            (datetime(2025, 1, 23, 14, 15), datetime(2025, 1, 23, 15, 0)),  # 14:15 - 15:00
            (datetime(2025, 1, 23, 14, 30), datetime(2025, 1, 23, 15, 15)),  # 14:30 - 15:15
            (datetime(2025, 1, 23, 14, 45), datetime(2025, 1, 23, 15, 30)),  # 14:45 - 15:30
            (datetime(2025, 1, 23, 16, 0), datetime(2025, 1, 23, 16, 45)),  # 16:00 - 16:45
            (datetime(2025, 1, 23, 16, 15), datetime(2025, 1, 23, 17, 0)),  # 16:15 - 17:00
        ]

        self.assertEqual(free_slots, expected_slots)


if __name__ == "__main__":
    unittest.main()
