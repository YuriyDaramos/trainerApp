from datetime import timedelta

import booking


def booking_time_discovery(trainer, service_id, date):
    trainer_schedule = trainer.models.TrainerSchedule.objects.filter(trainer=trainer, datetime_start__date=date)
    trainer_booking = booking.models.Booking.objects.filter(trainer=trainer, datetime_start__date=date)
    desired_service = trainer.models.Service.objects.get(pk=service_id)
    search_window = desired_service.duration
    free_slots = []
    for schedule in trainer_schedule:
        start_time = schedule.datetime_start
        end_time = start_time + timedelta(minutes=search_window)

        is_free = True
        for booking in trainer_booking:
            if not (end_time <= booking.datetime_start or start_time >= booking.datetime_end):
                is_free = False
                break

        if is_free:
            free_slots.append(start_time.strftime("%H:%M"))

    return free_slots
