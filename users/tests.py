from datetime import time, date, timedelta, datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client

from administrator.models import Schedule
from salon.models import Master, Services, Booking


class BookingTests(TestCase):
    def setUp(self):
        # Створюємо тестові дані
        self.master1 = Master.objects.create(name='Master 1')
        self.master2 = Master.objects.create(name='Master 2')

        self.user1 = User.objects.create_user(username='123', password='123')

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

    def test_free_time_for_booking(self):
        client = Client()
        client.login(username=self.user1.username, password='123')
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
        client.login(username=self.user1.username, password='123')
        info_about_booking = {'time': f'{date.today().strftime("%Y-%m-%d")} '
                                      f'{time(14, 0, 0).strftime("%H:%M:%S")} '
                                      f'{self.master1.id} '
                                      f'{self.service2.id}'}
        response = client.post('/end_booking/', info_about_booking)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Booking.objects.all()), 2)
