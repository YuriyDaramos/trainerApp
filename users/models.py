from django.contrib.auth.models import User
from django.db import models


class Rating(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='given_ratings')
    recipient = models.OneToOneField(User, on_delete=models.CASCADE, related_name='received_ratings')
    rate = models.IntegerField(default=0)
    text = models.CharField(max_length=512)


