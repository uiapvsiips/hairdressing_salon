from datetime import datetime, time, timedelta, date
from django.contrib.auth.models import User
from django.test import Client,TestCase
from administrator.models import Schedule
from .models import Booking, Master, Services
from .schedule_worker import calc_breaks


class CalcBreaksTestCase(TestCase):
    def setUp(self):
        self.master_start_time = datetime(2023, 4, 10, 9, 0)
        self.master_end_time = datetime(2023, 4, 10, 17, 0)
        self.service_duration = 60

    def test_no_bookings(self):
        free_gaps = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, [])
        self.assertEqual(len(free_gaps), 1)
        self.assertEqual(free_gaps[0]['start_time'], self.master_start_time)
        self.assertEqual(free_gaps[0]['end_time'], self.master_end_time - timedelta(minutes=self.service_duration))

    def test_first_booking(self):
        free_gaps = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, [])
        self.assertEqual(len(free_gaps), 1)
        self.assertEqual(free_gaps[0]['start_time'], self.master_start_time)
        self.assertEqual(free_gaps[0]['end_time'], self.master_end_time - timedelta(minutes=self.service_duration))

    def test_last_booking(self):
        new_booking_start_time = time(hour=9, minute=0)
        new_booking_end_time = time(hour=16, minute=0)
        new_booking = Booking(date=datetime.now().date(), start_time=new_booking_start_time,
                              end_time=new_booking_end_time)
        free_gaps = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, [new_booking])
        self.assertEqual(len(free_gaps), 1)
        self.assertEqual(free_gaps[0]['end_time'], self.master_end_time - timedelta(minutes=self.service_duration))

    def test_bookings_in_between(self):
        bookings_list = [
            Booking(date=date(2023, 4, 10), start_time=time(hour=10, minute=0), end_time=time(hour=11, minute=0)),
            Booking(date=date(2023, 4, 10), start_time=time(hour=13, minute=0), end_time=time(hour=14, minute=0)),
            Booking(date=date(2023, 4, 10), start_time=time(hour=15, minute=0), end_time=time(hour=16, minute=0)),
        ]
        free_gaps = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, bookings_list)
        self.assertEqual(len(free_gaps), 4)

    def test_one_booking(self):
        bookings_list = [Booking(date=datetime(2023, 4, 10), start_time=time(10, 0), end_time=time(11, 0))]

        expected_result = [
            {'start_time': self.master_start_time,
             'end_time': datetime(2023, 4, 10, 10, 0) - timedelta(minutes=self.service_duration)},
            {'start_time': datetime(2023, 4, 10, 11, 0),
             'end_time': self.master_end_time - timedelta(minutes=self.service_duration)}]

        result = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, bookings_list)

        self.assertEqual(result, expected_result)

    def test_multiple_bookings(self):
        bookings_list = [Booking(date=date(2023, 4, 10), start_time=time(10, 0), end_time=time(11, 0)),
                         Booking(date=date(2023, 4, 10), start_time=time(13, 0), end_time=time(14, 0))]
        expected_result = [
            {'start_time': self.master_start_time,
             'end_time': datetime(2023, 4, 10, 10, 0) - timedelta(minutes=self.service_duration)},
            {'start_time': datetime(2023, 4, 10, 11, 0),
             'end_time': datetime(2023, 4, 10, 13, 0) - timedelta(minutes=self.service_duration)},
            {'start_time': datetime(2023, 4, 10, 14, 0),
             'end_time': self.master_end_time - timedelta(minutes=self.service_duration)}]

        result = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, bookings_list)

        self.assertEqual(result, expected_result)


class HandlersTests(TestCase):
    def setUp(self):
        # Створюємо тестові дані
        self.master1 = Master.objects.create(name='Master 1')
        self.master2 = Master.objects.create(name='Master 2')

        self.user1 = User.objects.create(username=123)

        self.service1 = Services.objects.create(name='Укладка волос', master=self.master1, price=1, duration=60)
        self.service2 = Services.objects.create(name='Окрашивание волос', master=self.master1, price=1, duration=120)
        self.service3 = Services.objects.create(name='Мужская стрижка', master=self.master2, price=1, duration=180)

        self.master1.services.set([self.service1, self.service2])
        self.master2.services.set([self.service2, self.service3])

        self.schedule1 = Schedule.objects.create(date=date.today(), master=self.master1, start_time='10:00',
                                                 end_time='17:00')
        self.schedule2 = Schedule.objects.create(date=date.today(), master=self.master2, start_time='10:00',
                                                 end_time='17:00')
        self.schedule3 = Schedule.objects.create(date=date.today() + timedelta(days=1), master=self.master1,
                                                 start_time='14:00', end_time='17:00')
        self.schedule4 = Schedule.objects.create(date=date.today() + timedelta(days=2), master=self.master2,
                                                 start_time='12:00', end_time='17:00')
        self.ms = self.master1.master_services_set.first()
        self.booking1 = Booking.objects.create(master=self.master1, service=self.master1.master_services_set.last(),
                                               user=self.user1, date=date.today(),
                                               start_time=time(10, 0, 0), end_time=time(11, 0, 0))

    def test_services_for_week_handler(self):
        client = Client()
        response = client.post('/services/')
        self.assertEqual(response.status_code, 200)
        expected_services = {self.service1, self.service2, self.service3}
        actual_services = set(response.context['unique_services_for_week'])
        self.assertEqual(actual_services, expected_services)

    def test_specialists_for_week_handler(self):
        client = Client()
        response = client.post('/specialist/')
        self.assertEqual(response.status_code, 200)
        expected_specialistss = {self.master1, self.master2}
        actual_specialistss = set(response.context['specialists'])
        self.assertEqual(expected_specialistss, actual_specialistss)

    def test_some_specialist_handler(self):
        client = Client()
        response = client.post(f'/specialist/{self.master1.id}/')
        self.assertEqual(response.status_code, 200)
        expected_services = set(self.master1.services.all())
        actual_services = set(response.context['services'])
        self.assertEqual(expected_services, actual_services)

    def test_free_time_for_booking(self):
        client = Client()
        input_data_for_all_specialists = {
            'date': datetime.today().strftime('%Y-%m-%d'),
            'service_id': self.service2.id
        }
        response = client.post('/booking/', input_data_for_all_specialists)
        self.assertEqual(response.status_code, 200)
        expected_time_vars = [
            '10:00:00 2 2', '10:15:00 2 2', '10:30:00 2 2', '10:45:00 2 2',
            '11:00:00 1 2', '11:15:00 1 2', '11:30:00 1 2', '11:45:00 1 2',
            '12:00:00 1 2', '12:15:00 1 2', '12:30:00 1 2', '12:45:00 1 2',
            '13:00:00 1 2', '13:15:00 1 2', '13:30:00 1 2', '13:45:00 1 2',
            '14:00:00 1 2', '14:15:00 1 2', '14:30:00 1 2', '14:45:00 1 2',
            '15:00:00 1 2'
        ]
        actual_time_vars = response.context['all_time_vars']
        self.assertListEqual(expected_time_vars, actual_time_vars)

    def test_save_booking(self):
        # Перевіряємо, що перед тестом був лише 1 букінг
        self.assertEqual(len(Booking.objects.all()), 1)
        client = Client()
        info_about_booking = {'time': f'{date.today().strftime("%Y-%m-%d")} ' \
                                      f'{time(14, 0, 0).strftime("%H:%M:%S")} ' \
                                      f'{self.master1.id} ' \
                                      f'{self.service2.id}'}
        response = client.post('/end_booking/', info_about_booking)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Booking.objects.all()),2)
