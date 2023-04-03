from django.db.models import Count, Max, Min
from django.shortcuts import render, redirect
from django.http import HttpResponse
from salon.models import Services, Master, Master_Services
from administrator.models import Schedule
from datetime import datetime, timedelta
from salon.models import Booking
from salon.schedule_worker import get_time_vars_for_service, sort_key


def user(request):
    return HttpResponse('your bookings will be here')


def booking(request):
    if request.POST:
        booking_date = request.POST.get('date')
        service_id = request.POST.get('service_id')
        all_time_vars = []
        if not request.POST.get('specialist_id'):
            masters_for_service = Master.objects.filter(master_services__service=service_id).all()
        else:
            specialist_id = request.POST.get('specialist_id')
            masters_for_service = []
            masters_for_service.append(Master.objects.get(id=specialist_id))
        for master in masters_for_service:
            current_master_time_vars = get_time_vars_for_service(master.id, booking_date, service_id)
            for current_time_var in current_master_time_vars:
                if not all_time_vars:
                    all_time_vars+=current_master_time_vars
                    break
                if not current_time_var.split(' ')[0] in [time_var.split(' ')[0] for time_var in all_time_vars]:
                    all_time_vars.append(current_time_var)
        sorted_vars = sorted(all_time_vars, key=sort_key)
    return render(request, 'end_booking.html', {'date': booking_date, 'all_time_vars':sorted_vars})

def end_booking(request):
    info_about_booking = request.POST['time'].split(' ')
    date = info_about_booking[0]
    time = info_about_booking[1]
    master_id = info_about_booking[2]
    service_id = info_about_booking[3]
    master = Master.objects.get(id=master_id)
    service = Services.objects.get(id=service_id)
    master_service = Master_Services.objects.get(master_id=master_id, service_id=service_id)
    start_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(minutes=service.duration)

    str_start_time = start_time.time().strftime("%H:%M:%S")
    new_booking = Booking(master=master, service=master_service, user_id=1, date=start_time.date(),
                          start_time=start_time.time(), end_time=end_time.time())
    # new_booking = Booking(master=master, service=master_service, user_id=1, date=start_time.date(),
    #                                         start_time='09:00:00', end_time='09:45:00')
    new_booking.save()
    d=1
    return HttpResponse('OK')


def login(request):
    return HttpResponse('Login page')


def register(request):
    return HttpResponse('Register page')

