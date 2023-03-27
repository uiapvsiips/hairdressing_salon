from django.db import models
from salon.models import Master

class Schedule(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


