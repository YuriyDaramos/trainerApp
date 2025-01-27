from datetime import timedelta, datetime

from django.utils import timezone

import trainer.models
from booking.models import Booking

import calendar
from datetime import datetime


def is_booking_conflict(current_start, current_end, trainer_booking, date):
    """
    Проверка на пересечение текущего времени с уже забронированными слотами.
    """
    for booking in trainer_booking:
        if booking.datetime_start.date() == date and booking.status != "canceled":
            if not (current_end <= booking.datetime_start or current_start >= booking.datetime_end):
                return True
    return False


def booking_time_discovery(trainer_id, service_id, date):
    trainer_schedule = trainer.models.TrainerSchedule.objects.filter(trainer_id=trainer_id, datetime_start__date=date)

    trainer_booking = Booking.objects.filter(trainer=trainer_id, datetime_start__date=date, status=True)

    desired_service = trainer.models.Service.objects.get(pk=service_id)
    search_window = desired_service.duration
    timestep = 15  # минуты

    free_slots = []
    current_time = datetime.now()
    for schedule in trainer_schedule:  # на тот случай, если рабочий день прерывается, например, перерывом на обед
        schedule_start = schedule.datetime_start
        schedule_end = schedule.datetime_end

        current_start = schedule_start
        while current_start + search_window <= schedule_end:
            current_end = current_start + search_window

            if current_end <= current_time:
                current_start += timedelta(minutes=timestep)
                continue

            if not is_booking_conflict(current_start, current_end, trainer_booking, date):
                free_slots.append((current_start, current_end))

            current_start += timedelta(minutes=timestep)

    return free_slots


def generate_month_days(year, month):
    """
    Генерирует массив чисел текущего месяца для отображения в календаре.

    :param year: Год
    :param month: Месяц
    :return: Список списков (строки таблицы календаря)
    """

    _, num_days = calendar.monthrange(year, month)
    first_day_of_month = datetime(year, month, 1).weekday()  # 0 - Понедельник, 6 - Воскресенье

    # Список дней
    days = [None] * first_day_of_month
    days += list(range(1, num_days + 1))

    while len(days) % 7 != 0:
        days.append(None)

    # Разбивка на недели (по 7 элементов в каждой)
    calendar_rows = [days[i:i + 7] for i in range(0, len(days), 7)]

    return calendar_rows


def generate_actual_calendar(current_year, current_month, selected_day):
    calendar_rows = generate_month_days(current_year, current_month)
    today = datetime.today().date()

    for week in calendar_rows:
        for day_number in week:
            if day_number:
                day_date = datetime(current_year, current_month, day_number).date()
                day_data = {
                    "number": day_number,
                    "is_valid": True,
                    "is_unavailable": False,
                }

                if day_date.weekday() >= 5:  # Суббота/воскресенье
                    day_data["is_holiday"] = True

                if day_date < today:
                    day_data["is_unavailable"] = True

                if selected_day and day_number == selected_day.day and current_month == selected_day.month and current_year == selected_day.year:
                    day_data["is_selected"] = True

                week[week.index(day_number)] = day_data
            else:
                week[week.index(day_number)] = {"is_valid": False}

    return calendar_rows
