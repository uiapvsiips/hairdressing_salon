from django.db import models
from salon.models import Master
from datetime import datetime

class Schedule(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def is_working(self, booking_time):
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)

        if start <= booking_time <= end:
            return True
        else:
            return False
