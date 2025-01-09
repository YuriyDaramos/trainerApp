from django.contrib.auth.models import User
from django.db import models


class TrainerDescription(models.Model):
    text = models.TextField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)


class TrainerSchedule(models.Model):
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)


class Category(models.Model):
    name = models.CharField(max_length=256)


class Service(models.Model):
    LEVEL_CHOICES = [(1, "Novice"),
                     (2, "Medium"),
                     (3, "Advanced"), ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.FloatField()
    level = models.IntegerField(choices=LEVEL_CHOICES)
    duration = models.DurationField()
