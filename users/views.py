from django.db.models import Count, Max, Min
from django.shortcuts import render, redirect
from django.http import HttpResponse
from salon.models import Services, Master, Master_Services
from administrator.models import Schedule
from datetime import datetime, timedelta


def user(request):
    return HttpResponse('your bookings will be here')


def booking(request):
    return render(request, 'booking.html')



def login(request):
    return HttpResponse('Login page')


def register(request):
    return HttpResponse('Register page')


def booking_specialists(request):
    return render(request, 'booking_specialists.html')


def booking_services(request):
    services = Services.objects.all()
    return render(request, 'booking_services.html', {'services':services})


def booking_to_service(request, service_id):
    if request.POST:
        service = Services.objects.get(id=service_id)
        masters_for_service = Master_Services.objects.filter(service=service).values('master_id')
        date = request.POST['date']
        min_time = Schedule.objects.filter(date=date, master_id__in=masters_for_service).aggregate(Min('start_time'))
        max_time = Schedule.objects.filter(date=date, master_id__in=masters_for_service).aggregate(Max('end_time'))
        time_intervals = []
        start_time = datetime.strptime(str(min_time['start_time__min']), '%H:%M:%S')
        end_time = datetime.strptime(str(max_time['end_time__max']), '%H:%M:%S')
        current_interval = start_time
        while current_interval < end_time:
            time_intervals.append(current_interval.strftime('%H:%M'))
            current_interval += timedelta(minutes=service.duration+10)
        return render(request, 'booking_service.html', {'date': date, 'time_intervals':time_intervals})
    else:
        return render(request, 'booking_service.html')


def booking_to_specialist(request, specialist_id):
    return None


def end_service_booking(request, service_id):
    if request.POST:
        masters_for_service = Master_Services.objects.filter(service_id=service_id).values('master_id')
        booking_datetime = datetime.strptime(request.POST['time'], '%Y-%m-%d %H:%M')
        # booking_time = datetime.strptime(datetime.today().date()+booking_datetime.split(' ')[1], '%Y-%M-%D%H:%M')
        booking_date =  request.POST['time'].split(' ')[0]
        chosen_master = Schedule.objects.filter(master_id__in=masters_for_service, date=booking_date).order_by('?').all()
        for master in chosen_master:
            boo = master.is_working(booking_datetime)
            d=1
            if boo:
                break
    return redirect('.')


def end_specialist_booking(request):
    return None