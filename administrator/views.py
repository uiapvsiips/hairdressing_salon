from django.shortcuts import render, redirect
from django.http import HttpResponse
from salon.models import Services, Master, Master_Services

# Create your views here.
def panel(request):
    return render(request, 'admin_panel.html')


def bookings(request):
    return HttpResponse('Admin panel->bookings')


def specialists(request):
    specialists = Master.objects.all()
    services = Services.objects.all()
    if request.method == 'POST':
        name = request.POST.get('specialist_name')
        phone = request.POST.get('specialist_phone')
        rank = request.POST.get('specialist_rank')
        new_specialist = Master(name=name, phone=phone, rank=rank)
        choosen_services = [service for service in request.POST if service.startswith('service_')]
        new_specialist.save()
        new_specialist.services.add(*[int(service.split('_')[1]) for service in choosen_services])
    return render(request, 'admin_specialists.html', context={'specialists': specialists, 'services': services})


def specialist_id_handler(request, specialist_id):
    specialist = Master.objects.filter(id=specialist_id).first()
    if request.method == 'POST':
        specialist.name = request.POST.get('specialist_name')
        specialist.phone = request.POST.get('specialist_phone')
        specialist.rank = request.POST.get('specialist_rank')
        specialist.status = request.POST.get('specialist_status')
        specialist.save()
        choosen_services = [service for service in request.POST if service.startswith('service_')]
        specialist.services.add(*[int(service.split('_')[1]) for service in choosen_services])
        specialist_services = Master_Services.objects.filter(master=specialist).all()
        specialist_services.exclude(service_id__in=[int(service.split('_')[1]) for service in choosen_services]).delete()
    specialist_services = Services.objects.filter(id__in=specialist.services.all())
    no_specialist_services = Services.objects.exclude(id__in=specialist.services.all())
    return render(request, 'admin_specialist.html', context={'specialist': specialist,'specialist_services': specialist_services,'no_specialist_services': no_specialist_services})


def services_handler(request):
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        new_service = Services(name=service_name, price=price, duration=duration)
        new_service.save()
    services = Services.objects.all()
    return render(request, 'admin_services.html', context={'services': services})

def service_id_handler(request, service_id):
    service = Services.objects.filter(id=service_id).first()
    if request.method == 'POST':
        service.name = request.POST.get('service_name')
        service.price = request.POST.get('price')
        service.duration = request.POST.get('duration')
        service.save()
    return render(request, 'admin_service.html', context={'service': service})