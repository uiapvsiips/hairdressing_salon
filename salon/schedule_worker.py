from datetime import datetime, timedelta

from administrator.models import Schedule
from salon.models import Master, Booking, Services


def __get_free_gaps_in_schedule(master_id, booking_date, service_id):
    # Вибираємо майстра, послугу, яку він повинен надати, розклад майстра на визначену дату, а також
    # бронювання до вказаного майстра на визначену дату
    master = Master.objects.get(id=master_id)
    service = Services.objects.get(id=service_id)
    masters_schedule = Schedule.objects.get(date=booking_date, master=master)
    masters_bookings_to_date = Booking.objects.filter(master=master, date=booking_date).order_by('start_time').all()
    bookings_to_date_count = len(masters_bookings_to_date)

    # Робимо змінні початку та кінця робочого дня майстра
    masters_begin_time = datetime.combine(masters_schedule.date, masters_schedule.start_time)
    masters_end_time = datetime.combine(masters_schedule.date, masters_schedule.end_time)

    # Створюємо змінну, в яку будемо вносити "віконця" майстра
    free_gaps_in_schedule = []

    # Якщо на вибрану дату до майстра відсутні бронювання, то у вільні проміжки вносимо весь день роботи майстра.
    # При цьому враховуємо максимально можливий час бронювання (кінець робочого дня майстра мінус час виконання послуги)
    if bookings_to_date_count==0:
        free_gaps_in_schedule.append({'start_time': masters_begin_time,
                                   'end_time': masters_end_time-timedelta(minutes=service.duration)})
    else:
        # Проходимо циклом по наявних бронюваннях до майстра на певну дату.
        for i in range(0, bookings_to_date_count):
            #  Визначаємо початок та кінець бронювання у форматі datetime
            booking_start_time = datetime.combine(masters_bookings_to_date[i].date,
                                                         masters_bookings_to_date[i].start_time)
            booking_end_time = datetime.combine(masters_bookings_to_date[i].date,
                                                       masters_bookings_to_date[i].end_time)

            # Якщо це перше бронювання на день, то дивимось, чи є час від початку робочого дня майстра до початку
            # поточного бронювання, аби записатися на послугу.
            if i == 0:
                break_duration = __get_break_duration(booking_start_time, masters_begin_time)
                break_start_time = masters_begin_time
                break_end_time = booking_start_time - timedelta(minutes=service.duration)
                if __is_longer_break(break_duration, service_duration=service.duration):
                    free_gaps_in_schedule.append({'start_time': break_start_time,
                                           'end_time': break_end_time})

            # Якщо це останнє бронювання на день (з 14:00 до 15:00), то дивимось, чи є час від кінця поточного
            # бронювання (15:00) до кінця робочого дня майстра (17:00) з урахуванням часу надання послуги
            # (якщо більше 2 годин - не показуємо).
            if i == bookings_to_date_count - 1:
                break_duration = __get_break_duration(masters_end_time, booking_end_time)
                break_start_time = booking_end_time
                break_end_time = masters_end_time - timedelta(minutes=service.duration)

            # В будь якому іншому випадку (вікна між бронюваннями) дивимось, чи вистачає часу від часу закінчення
            # попередньої послуги (12:00) до часу початку наступної (14:00).
            else:
                next_booking_start_time = datetime.combine(masters_bookings_to_date[i].date,
                                                           masters_bookings_to_date[i + 1].start_time)
                break_duration = __get_break_duration(next_booking_start_time, booking_end_time)
                break_start_time = booking_end_time
                break_end_time = next_booking_start_time - timedelta(minutes=service.duration)

            # Якщо час перерви між бронюваннями більший, аніж час, необхідний на виконання послуги, вносимо це
            # "віконце" до списку
            if __is_longer_break(break_duration, service_duration=service.duration):
                free_gaps_in_schedule.append({'start_time': break_start_time,
                                       'end_time': break_end_time})

    return free_gaps_in_schedule


def __is_longer_break(break_duration, service_duration):
    return True if (break_duration - timedelta(minutes=service_duration)) >= timedelta(seconds=0) else False


def __get_break_duration(next_booking_start_time, prev_booking_end_time):
    break_duration = next_booking_start_time - prev_booking_end_time
    return break_duration

def get_time_vars_for_service(master_id, booking_date, service_id):
    # Отримуємо "віконця" майстра, які по часу дозволяють надати послугу
    free_gaps_in_schedule = __get_free_gaps_in_schedule(master_id, booking_date, service_id)
    time_vars = []

    # Проходимо циклом по кожному "віконцю" та дивимось, чи можемо ми надати клієнту варіаціі по часу на запис з
    # інтервалом в 15 хвилин.
    # Наприклад: якщо вільне віконце у майстра з 09:00 до 10:00, а послуга триває одну годину - запис тільки на 09:00.
    # Але якшо віконце з 09:00 до 11:00, то клієнт може записатися на 09:00, 09:15, 09:30, 09:45, 10:00.
    for gap_in_schedule in free_gaps_in_schedule:
        start_time = gap_in_schedule['start_time']
        end_time = gap_in_schedule['end_time']
        interval = timedelta(minutes=15)
        current_time = start_time
        while current_time <= end_time:
            time_vars.append(current_time.strftime("%H:%M:%S"))
            current_time += interval
    return time_vars
