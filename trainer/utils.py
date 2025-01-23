from datetime import timedelta, datetime

import trainer.models
from booking.models import Booking


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
    trainer_schedule = trainer.models.TrainerSchedule.objects.filter(trainer_id=trainer_id)
    trainer_booking = Booking.objects.filter(trainer=trainer_id, datetime_start__date=date, status=True)

    desired_service = trainer.models.Service.objects.get(pk=service_id)
    search_window = desired_service.duration
    timestep = 15  # минуты

    free_slots = []
    for schedule in trainer_schedule:   # на тот случай, если рабочий день прерывается, например, перерывом на обед
        schedule_start = schedule.datetime_start
        schedule_end = schedule.datetime_end

        current_start = schedule_start
        while current_start + search_window <= schedule_end:
            current_end = current_start + search_window

            if not is_booking_conflict(current_start, current_end, trainer_booking, date):
                free_slots.append((current_start, current_end))

            current_start += timedelta(minutes=timestep)

    return free_slots
