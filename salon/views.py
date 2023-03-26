from django.shortcuts import render
from django.http import HttpResponse
from salon.models import Services, Master

def services_handler(request):
    services = Services.objects.all()
    return HttpResponse('Services page')


def service_id_handler(request, service_id):
    return HttpResponse(f'Service id: {service_id}')


def specialist_id_handler(request, specialist_id):
    return HttpResponse(f'Specialist id: {specialist_id}')



def specialist_handler(request):
    return HttpResponse(f'Specialists page')