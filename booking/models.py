from django.contrib.auth.models import User
from django.db import models

from trainer.models import Service


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_as_user')
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings_as_trainer')
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
