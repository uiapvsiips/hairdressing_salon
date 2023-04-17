from datetime import datetime, timedelta

from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect

from salon.models import Booking
from salon.models import Services, Master, Master_Services
from salon.schedule_worker import get_time_vars_for_service, sort_key


def user(request):
    return HttpResponse('your bookings will be here')


@login_required(login_url='/login/')
def booking(request):
    if request.POST:
        booking_date = request.POST.get('date')
        service_id = request.POST.get('service_id')
        all_time_vars = []
        if not request.POST.get('specialist_id'):
            masters_for_service = Master.objects.filter(master_services__service=service_id).all()
        else:
            specialist_id = request.POST.get('specialist_id')
            masters_for_service = [Master.objects.get(id=specialist_id)]
        for master in masters_for_service:
            current_master_time_vars = get_time_vars_for_service(master.id, booking_date, service_id)
            for current_time_var in current_master_time_vars:
                if not all_time_vars:
                    all_time_vars += current_master_time_vars
                    break
                if not current_time_var.split(' ')[0] in [time_var.split(' ')[0] for time_var in all_time_vars]:
                    all_time_vars.append(current_time_var)
        sorted_vars = sorted(all_time_vars, key=sort_key)
        return render(request, 'end_booking.html',
                      {'date': booking_date, 'all_time_vars': sorted_vars, 'service': service_id})


@login_required(login_url='/login/')
def end_booking(request):
    info_about_booking = request.POST['time'].split(' ')
    date = info_about_booking[0]
    time = info_about_booking[1]
    master_id = info_about_booking[2]
    service_id = info_about_booking[3]
    master = Master.objects.get(id=master_id)
    service = Services.objects.get(id=service_id)
    master_service = Master_Services.objects.get(master_id=master_id, service_id=service_id)
    start_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(minutes=service.duration)
    new_booking = Booking(master=master, service=master_service, user_id=1, date=start_time.date(),
                          start_time=start_time.time(), end_time=end_time.time())
    try:
        new_booking.save()
    except Exception as e:
        return HttpResponseServerError(e)
    return HttpResponse(
        f'Заброньовано! Спеціаліст {master.name}. Дата:{start_time.date()}. Час бронювання: {start_time.time()}.')


def login_handler(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POSTget('password')
        login_user = authenticate(request, username=username, password=password)
        if login_user is not None:
            login(request, login_user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')


def register_handler(request):
    if request.method == 'GET':
        return render(request, 'registration.html')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')
    if password != confirm_password:
        return HttpResponse(status=500)
    new_user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                        last_name=last_name)
    new_user.is_active = False
    try:
        new_user.save()
        return redirect('/login/')
    except Exception as e:
        return HttpResponseServerError(e)


def logout_handler(request):
    logout(request)
    return redirect('/')
