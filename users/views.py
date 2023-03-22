from django.shortcuts import render, redirect
from django.http import HttpResponse
# Create your views here.
def user(request):
    return HttpResponse('your bookings will be here')


def booking(request):
    if request.method=='POST':
        return HttpResponse('your bookings will be here')
    return redirect('/user/')


def login(request):
    return HttpResponse('Login page')


def register(request):
    return HttpResponse('Register page')