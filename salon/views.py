from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from salon.models import Services, Master
from administrator.models import Schedule
from datetime import datetime, timedelta
from salon.schedule_worker import get_time_vars_for_service

@login_required(login_url='/login/')
def services_handler(request):
    today = datetime.today().date()
    seven_days = today + timedelta(days=7)

    # Get schedule for a week and get unique masters_ids from there
    sсhedule_on_week = Schedule.objects.filter(date__gte=today, date__lte=seven_days).order_by('date','master_id', 'start_time')
    masters_for_week = set([schedule.master_id for schedule in sсhedule_on_week])

    # Get services for a week and get unique service_ids from there
    services_for_week = Services.objects.filter(master__services__master__in=masters_for_week)
    unique_services_for_week = set([service for service in services_for_week])

    return render(request, 'services.html', {'unique_services_for_week': unique_services_for_week})

@login_required(login_url='/login/')
def service_id_handler(request, service_id):
    return render(request, 'booking_service.html', {"service_id":service_id})

@login_required(login_url='/login/')
def specialist_id_handler(request, specialist_id):
    specialist = Master.objects.get(id=specialist_id)
    services = Services.objects.filter(master_services__master_id=specialist.id).all()
    return render(request, 'booking_specialist.html', {"services":services, 'specialist_id':specialist_id})


@login_required(login_url='/login/')
def specialist_handler(request):
    specialists = Master.objects.filter(status=0).all()
    return render(request, 'booking_specialists.html', {"specialists":specialists})


def root_handler(request):
    return render(request, 'main.html')