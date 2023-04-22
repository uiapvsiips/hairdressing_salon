from datetime import time, date, timedelta, datetime

from django.contrib.auth.models import User
from django.test import TestCase, Client

from administrator.models import Schedule
from salon.models import Master, Services, Booking, Master_Services


class BookingTests(TestCase):
    fixtures = ['fixtures_for_user_and_admin.json']

    def setUp(self):
        # Створюємо тестові дані
        self.master1 = Master.objects.first()
        self.master1_schedule = Schedule.objects.create(date=date.today(), master=self.master1, start_time='10:00',
                                                        end_time='17:00')
        self.user1 = User.objects.create_user(username='123', password='123')
        self.service1 = Services.objects.get(id=Master_Services.objects.filter(master=self.master1).last().id)

    def test_free_time_for_booking(self):
        client = Client()
        client.login(username=self.user1.username, password='123')
        input_data_for_all_specialists = {
            'date': datetime.today().strftime('%Y-%m-%d'),
            'service_id': self.service1.id,
            'specialist_id': self.master1.id
        }
        response = client.post('/booking/', input_data_for_all_specialists)
        self.assertEqual(response.status_code, 200)
        expected_time_vars = [
            f'10:00:00 {self.master1.id} {self.service1.id}', f'10:15:00 {self.master1.id} {self.service1.id}',
            f'10:30:00 {self.master1.id} {self.service1.id}', f'10:45:00 {self.master1.id} {self.service1.id}',
            f'11:00:00 {self.master1.id} {self.service1.id}', f'11:15:00 {self.master1.id} {self.service1.id}',
            f'11:30:00 {self.master1.id} {self.service1.id}', f'11:45:00 {self.master1.id} {self.service1.id}',
            f'12:00:00 {self.master1.id} {self.service1.id}', f'12:15:00 {self.master1.id} {self.service1.id}',
            f'12:30:00 {self.master1.id} {self.service1.id}', f'12:45:00 {self.master1.id} {self.service1.id}',
            f'13:00:00 {self.master1.id} {self.service1.id}', f'13:15:00 {self.master1.id} {self.service1.id}',
            f'13:30:00 {self.master1.id} {self.service1.id}', f'13:45:00 {self.master1.id} {self.service1.id}',
            f'14:00:00 {self.master1.id} {self.service1.id}', f'14:15:00 {self.master1.id} {self.service1.id}',
            f'14:30:00 {self.master1.id} {self.service1.id}', f'14:45:00 {self.master1.id} {self.service1.id}',
            f'15:00:00 {self.master1.id} {self.service1.id}'
        ]
        actual_time_vars = response.context['all_time_vars']
        self.assertListEqual(expected_time_vars, actual_time_vars)

    def test_save_booking(self):
        # Перевіряємо, що перед тестом був лише 1 букінг
        self.assertEqual(len(Booking.objects.all()), 0)
        client = Client()
        client.login(username=self.user1.username, password='123')
        info_about_booking = {'time': f'{date.today().strftime("%Y-%m-%d")} '
                                      f'{time(14, 0, 0).strftime("%H:%M:%S")} '
                                      f'{self.master1.id} '
                                      f'{self.service1.id}'}
        response = client.post('/end_booking/', info_about_booking)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Booking.objects.all()), 1)
