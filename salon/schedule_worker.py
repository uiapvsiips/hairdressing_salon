from datetime import datetime, timedelta

from administrator.models import Schedule
from salon.models import Master, Booking, Services


def get_free_gaps_in_schedule(master_id, booking_date, service_id):
    # Вибираємо майстра, послугу, яку він повинен надати, розклад майстра на визначену дату, а також
    # бронювання до вказаного майстра на визначену дату
    master = Master.objects.get(id=master_id)
    service = Services.objects.get(id=service_id)
    masters_schedule = Schedule.objects.get(date=booking_date, master=master)
    masters_bookings_to_date = Booking.objects.filter(master=master, date=booking_date).order_by('start_time').all()
    bookings_to_date_count = len(masters_bookings_to_date)

    # Визначаємо початковий (початок робочога дня майстра) та останній можливий час запису до майстра
    # (кінець робочого дня майстра мінус час виконання послуги).
    first_service_time = datetime.combine(masters_schedule.date, masters_schedule.start_time)
    last_service_time = datetime.combine(masters_schedule.date, masters_schedule.end_time)
    masters_gaps = []

    for i in range(0, bookings_to_date_count):
        master_booking_start_time = datetime.combine(masters_bookings_to_date[i].date,
                                                     masters_bookings_to_date[i].start_time)
        master_booking_end_time = datetime.combine(masters_bookings_to_date[i].date,
                                                   masters_bookings_to_date[i].end_time)
        if i == 0:
            if ((master_booking_start_time - first_service_time) - timedelta(minutes=service.duration)) > timedelta(
                    seconds=1):
                masters_gaps.append({'start_time': first_service_time,
                                     'end_time': master_booking_start_time})
        elif i == bookings_to_date_count - 1:
            if ((last_service_time - master_booking_end_time) - timedelta(minutes=service.duration)) > timedelta(
                    seconds=1):
                masters_gaps.append({'start_time': master_booking_end_time,
                                     'end_time': last_service_time - timedelta(minutes=service.duration)})
        else:
            next_master_booking_start_time = datetime.combine(masters_bookings_to_date[i].date,
                                                              masters_bookings_to_date[i + 1].start_time)
            if ((master_booking_end_time - next_master_booking_start_time) - timedelta(
                    minutes=service.duration)) > timedelta(seconds=1):
                masters_gaps.append({'start_time': first_service_time,
                                     'end_time': next_master_booking_start_time})
    d = 1
