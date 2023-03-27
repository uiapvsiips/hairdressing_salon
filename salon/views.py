from django.shortcuts import render
from django.http import HttpResponse
from salon.models import Services, Master
from administrator.models import Schedule
from datetime import datetime, timedelta

def services_handler(request):
    today = datetime.today()
    seven_days = today + timedelta(days=7)
    sсhedule_on_week = Schedule.objects.filter(date__gte=today, date__lte=seven_days)
    for g in sсhedule_on_week:
        b=1
    services = Services.objects.all()
    datetime.now()
    for service in services:
        b=1

    return HttpResponse('Services page')


def service_id_handler(request, service_id):
    return HttpResponse(f'Service id: {service_id}')


def specialist_id_handler(request, specialist_id):
    return HttpResponse(f'Specialist id: {specialist_id}')



def specialist_handler(request):
    return HttpResponse(f'Specialists page')