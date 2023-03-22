from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def abc(request):
    return HttpResponse("123")


def services_handler(request):
    return HttpResponse('services')


def service_id_handler(request, service_id):
    return HttpResponse(service_id)