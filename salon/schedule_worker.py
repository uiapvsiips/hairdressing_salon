from datetime import datetime, timedelta

from administrator.models import Schedule
from salon.models import Master, Booking, Services


def __get_info_for_calc(master_id, booking_date, service_id):
    # Вибираємо майстра, послугу, яку він повинен надати, розклад майстра на визначену дату, а також
    # бронювання до вказаного майстра на визначену дату
    master = Master.objects.get(id=master_id)
    service = Services.objects.get(id=service_id)
    masters_schedule = Schedule.objects.filter(date=booking_date, master=master).first()

    # Якщо майстер в цей день не працює - повертаємо пустий ліст
    if not masters_schedule:
        return []

    # Вибираємо з бази всі записи до майстра на дату.
    masters_bookings_to_date = Booking.objects.filter(master=master, date=booking_date).order_by('start_time').all()

    # Робимо змінні початку та кінця робочого дня майстра у datetime(для подальшого виклику функції timedelta)
    masters_begin_time = datetime.combine(masters_schedule.date, masters_schedule.start_time)
    masters_end_time = datetime.combine(masters_schedule.date, masters_schedule.end_time)
    return {
        'master_start_time': masters_begin_time,
        'master_end_time': masters_end_time,
        'service_duration': service.duration,
        'bookings_list': masters_bookings_to_date
    }


def calc_breaks(master_start_time: datetime, master_end_time: datetime, service_duration:int, bookings_list:list):
    free_gaps_in_schedule = []
    if len(bookings_list) == 0:
        free_gaps_in_schedule.append({'start_time': master_start_time,
                                      'end_time': master_end_time - timedelta(minutes=service_duration)})
    else:
        for i in range(0, len(bookings_list)):
            #  Визначаємо початок та кінець бронювання у форматі datetime
            booking_start_time = datetime.combine(bookings_list[i].date,
                                                  bookings_list[i].start_time)
            booking_end_time = datetime.combine(bookings_list[i].date,
                                                bookings_list[i].end_time)

            # Якщо це перше бронювання на день, то дивимось, чи є час від початку робочого дня майстра до початку
            # поточного бронювання, аби записатися на послугу.
            if i == 0:
                if _is_longer_break(booking_start_time, master_start_time, service_duration):
                    free_gaps_in_schedule.append({'start_time': master_start_time,
                                                  'end_time': booking_start_time - timedelta(minutes=service_duration)})

            # Якщо це останнє бронювання на день (наприклад, з 14:00 до 15:00), то дивимось, чи є час від кінця
            # поточного бронювання (15:00) до кінця робочого дня майстра (17:00) з урахуванням часу надання послуги
            # (якщо послуга надається понад 2 години - не показуємо).
            if i == len(bookings_list) - 1:
                if _is_longer_break(master_end_time, booking_end_time, service_duration):
                    free_gaps_in_schedule.append({'start_time': booking_end_time,
                                                  'end_time': master_end_time - timedelta(minutes=service_duration)})

            # В будь-якому іншому випадку (вікна між бронюваннями) дивимось, чи вистачає часу від часу закінчення
            # попередньої послуги (12:00) до часу початку наступної (14:00).
            else:
                if _is_longer_break(master_end_time, booking_end_time, service_duration):
                    free_gaps_in_schedule.append({'start_time': booking_end_time,
                                                  'end_time': (datetime.combine(bookings_list[i].date,
                                                                                bookings_list[
                                                                                    i + 1].start_time)) - timedelta(
                                                      minutes=service_duration)})
    return free_gaps_in_schedule


def _is_longer_break(next_booking_start_time, prev_booking_end_time, service_duration):
    break_duration = next_booking_start_time - prev_booking_end_time
    return True if (break_duration - timedelta(minutes=service_duration)) >= timedelta(seconds=0) else False


def get_time_vars_for_service(master_id, booking_date, service_id):
    # Отримуємо "віконця" майстра, які більше або дорівнюють часу надання послуги
    info_for_calc = __get_info_for_calc(master_id, booking_date, service_id)
    free_gaps_in_schedule = calc_breaks(**info_for_calc)

    time_vars = []

    # Проходимо циклом по кожному "віконцю" та дивимось, чи можемо ми надати клієнту варіації по часу на запис з
    # інтервалом в 15 хвилин.
    # Наприклад: якщо вільне віконце у майстра з 09:00 до 10:00, а послуга триває одну годину - запис тільки на 09:00.
    # Але якщо віконце з 09:00 до 11:00, то клієнт може записатися на 09:00, 09:15, 09:30, 09:45, 10:00.
    for gap_in_schedule in free_gaps_in_schedule:
        start_time = gap_in_schedule['start_time']
        end_time = gap_in_schedule['end_time']
        interval = timedelta(minutes=15)
        current_time = start_time
        while current_time <= end_time:
            time_vars.append(f'{current_time.strftime("%H:%M:%S")} {master_id} {service_id}')
            current_time += interval
    return time_vars


def sort_key(item):
    return item[:8]
