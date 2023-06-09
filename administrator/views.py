from datetime import datetime, timedelta

from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404
from administrator.models import Schedule
from salon.models import Services, Master, Master_Services, Booking


# Create your views here.
@user_passes_test(lambda u: u.groups.filter(name='administrator').exists(), login_url='/login/')
def panel(request):
    return render(request, 'admin_panel.html')


def bookings(request):
    return HttpResponse('Admin panel->bookings')

@user_passes_test(lambda u: u.groups.filter(name='administrator').exists(), login_url='/login/')
def specialists(request):
    specialists_list = Master.objects.all()
    paginator = Paginator(specialists_list, 2)
    page = request.GET.get('page')
    specialists = paginator.get_page(page)
    services = Services.objects.all()
    if request.method == 'POST':
        name = request.POST.get('specialist_name')
        phone = request.POST.get('specialist_phone')
        rank = request.POST.get('specialist_rank')
        new_specialist = Master(name=name, phone=phone, rank=rank)
        choosen_services = [service for service in request.POST if service.startswith('service_')]
        try:
            new_specialist.save()
        except Exception as e:
            return HttpResponseServerError(e)
        new_specialist.services.set(int(service.split('_')[1]) for service in choosen_services)
    return render(request, 'admin_specialists.html', context={'specialists': specialists, 'services': services})

@user_passes_test(lambda u: u.groups.filter(name='administrator').exists(), login_url='/login/')
def specialist_id_handler(request, specialist_id):
    specialist = get_object_or_404(Master, id=specialist_id)
    if request.method == 'POST':
        specialist.name = request.POST.get('specialist_name')
        specialist.phone = request.POST.get('specialist_phone')
        specialist.rank = request.POST.get('specialist_rank')
        specialist.status = request.POST.get('specialist_status')
        try:
            specialist.save()
        except Exception as e:
            return HttpResponseServerError(e)
        # Обираємо сервіси, які відмічені чекбоксом та додаємо їх для майстра
        choosen_services = [service.split('_')[1] for service in request.POST if service.startswith('service_')]
        specialist.services.set(choosen_services)
        # Виключаємо сервіси, які відмічені чекбоксом (отримуємо невідмічені), та видаляємо їх для цього майстра
        Master_Services.objects.filter(master=specialist).exclude(service__in=choosen_services).delete()
    specialist_schedule = Schedule.objects.filter(master=specialist,
                                                  date__gte=datetime.today() - timedelta(days=1)).all()
    specialist_services = Services.objects.filter(id__in=specialist.services.all())
    no_specialist_services = Services.objects.exclude(id__in=specialist.services.all())
    return render(request, 'admin_specialist.html', context={'specialist': specialist,
                                                             'specialist_services': specialist_services,
                                                             'no_specialist_services': no_specialist_services,
                                                             'specialist_schedule': specialist_schedule,
                                                             'today': datetime.today()})

@user_passes_test(lambda u: u.groups.filter(name='administrator').exists(), login_url='/login/')
def services_handler(request):
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        new_service = Services(name=service_name, price=price, duration=duration)
        try:
            new_service.save()
        except Exception as e:
            return HttpResponseServerError(e)
    services = Services.objects.all()
    return render(request, 'admin_services.html', context={'services': services})

@user_passes_test(lambda u: u.groups.filter(name='administrator').exists(), login_url='/login/')
def service_id_handler(request, service_id):
    service = get_object_or_404(Services, id=service_id)
    if request.method == 'POST':
        service.name = request.POST.get('service_name')
        service.price = request.POST.get('price')
        service.duration = request.POST.get('duration')
        try:
            service.save()
        except Exception as e:
            return HttpResponseServerError(e)
    return render(request, 'admin_service.html', context={'service': service})

@user_passes_test(lambda u: u.groups.filter(name='administrator').exists(), login_url='/login/')
def edit_schedule(request, specialist_id):
    # Видалення вже наявних розкладів
    Schedule.objects.filter(master=specialist_id).exclude(
        id__in=[date.split('_')[1] for date in request.POST if date.startswith('date')]).delete()
    # Редагування наявних розкладів
    current_schedules_ids = [date.split('_')[1] for date in request.POST if date.startswith('date_')]
    for current_schedule_id in current_schedules_ids:
        current_date = request.POST.get(f'date_{current_schedule_id}')
        current_start_time = request.POST.get(f'start_time_{current_schedule_id}')
        current_end_time = request.POST.get(f'end_time_{current_schedule_id}')
        schedule = Schedule.objects.get(id=current_schedule_id)
        schedule.date = current_date
        schedule.start_time = current_start_time
        schedule.end_time = current_end_time
        try:
            schedule.save()
        except Exception as e:
            return HttpResponseServerError(e)
    # Додавання нових розкладів
    new_schedules_count = len([date for date in request.POST if date.startswith('new_date')])
    for i in range(0, new_schedules_count):
        date = request.POST[f'new_date_{i}']
        start_time = request.POST[f'new_start_time_{i}']
        end_time = request.POST[f'new_end_time_{i}']
        new_schedule = Schedule(master_id=specialist_id, date=date, start_time=start_time, end_time=end_time)
        try:
            new_schedule.save()
        except Exception as e:
            return HttpResponseServerError(e)
    return redirect('.')

@user_passes_test(lambda u: u.groups.filter(name='administrator').exists(), login_url='/login/')
def masters_booking(request, specialist_id):
    date = request.GET.get('date')
    bookings = Booking.objects.filter(master=specialist_id, date=date).order_by('start_time')
    for booking in bookings:
        service = Services.objects.get(master_services=booking.service)
    return render(request, 'admin_specialist_bookings.html', {'bookings': bookings})