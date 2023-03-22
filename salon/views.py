from django.shortcuts import render
from django.http import HttpResponse

def services_handler(request):
    return HttpResponse('Services page')


def service_id_handler(request, service_id):
    return HttpResponse(f'Service id: {service_id}')


def specialist_id_handler(request, specialist_id):
    return HttpResponse(f'Specialist id: {specialist_id}')



def specialist_handler(request):
    return HttpResponse(f'Specialists page')