from django.shortcuts import render
from django.http import HttpResponse
from salon.models import Services, Master
from administrator.models import Schedule
from datetime import datetime, timedelta

def services_handler(request):
    today = datetime.today().date()
    seven_days = today + timedelta(days=7)

    # Get schedule for a week and get unique masters_ids from there
    sсhedule_on_week = Schedule.objects.filter(date__gte=today, date__lte=seven_days).order_by('date','master_id', 'start_time')
    masters_for_week = set([schedule.master_id for schedule in sсhedule_on_week])

    # Get services for a week and get unique service_ids from there
    services_for_week = Services.objects.filter(master__services__master__in=masters_for_week)
    unique_services_for_week = set([service for service in services_for_week])
    return render(request, 'services.html', context= {'unique_services_for_week': unique_services_for_week})
    return HttpResponse(f'Services for a week {unique_services_for_week}')


def service_id_handler(request, service_id):
    return HttpResponse(f'Service id: {service_id}')


def specialist_id_handler(request, specialist_id):
    return HttpResponse(f'Specialist id: {specialist_id}')



def specialist_handler(request):
    return HttpResponse(f'Specialists page')