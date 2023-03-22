from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def panel(request):
    return HttpResponse('Admin panel')


def bookings(request):
    return HttpResponse('Admin panel->bookings')


def specialists(request):
    return HttpResponse('Admin panel->specialists')


def specialist_id_handler(request, specialist_id):
    return HttpResponse(f'Admin panel->specialists id_handler {specialist_id}')