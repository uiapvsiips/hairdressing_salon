from django.contrib.auth.models import User
from django.db import models

class Services(models.Model):
    name = models.CharField(max_length=150)
    price = models.IntegerField()
    duration = models.IntegerField()

class Master(models.Model):
    RANK_CHOISES = (
        (0, 'zero rank'),
        (1, 'first rank'),
        (2, 'second rank'),
        (3, 'third rank')
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    status = models.IntegerField(default=0)
    rank = models.IntegerField(default=0, choices=RANK_CHOISES)
    services = models.ManyToManyField(Services, blank=True, through='Master_Services')


class Master_Services(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    service = models.ForeignKey(Services, on_delete=models.CASCADE)

class Booking(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    service = models.ForeignKey(Master_Services, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    status = models.IntegerField(default=0)
