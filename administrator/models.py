from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from salon.models import Master

class Schedule(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

@receiver(pre_delete, sender=Schedule)
def delete_bookings(sender, instance, **kwargs):
    instance.master.booking_set.filter(date=instance.date).delete()