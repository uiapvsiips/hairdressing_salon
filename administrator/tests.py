from datetime import date, timedelta

from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from .models import Schedule
from salon.models import Master, Services


class TetsAdminPanel(TestCase):
    fixtures = ['fixtures_for_user_and_admin.json']
    def setUp(self):
        self.master1 = Master.objects.first()

        self.user1 = User.objects.first()

        self.schedule1 = Schedule.objects.create(date=date.today(), master=self.master1, start_time='10:00',
                                                 end_time='17:00')
        self.schedule2 = Schedule.objects.create(date=date.today()+timedelta(days=1), master=self.master1, start_time='10:00',
                                                 end_time='17:00')

        self.service1 = Services.objects.create(name='Укладка волос', price=1, duration=60)
        self.service2 = Services.objects.create(name='Окрашивание волос', price=1, duration=120)
        self.service3 = Services.objects.create(name='Мужская стрижка', price=1, duration=180)

        self.master1.services.set([self.service1, self.service2, self.service3])



    def test_add_new_specialist(self):
        self.assertEqual(len(Master.objects.all()), 3)
        client = Client()
        client.login(username=self.user1.username, password='123')
        new_specialist_info = {
            'specialist_name': 'Master 2',
            'specialist_phone': '321',
            'specialist_rank': 1
        }
        response = client.post('/panel/specialists/', new_specialist_info)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Master.objects.all()), 4)

        # Перевіряємо, що поверне 500 код, якщо передати невалідні дані
        bad_new_specialist_info = {
            'specialist_name': 'Master 2',
            'specialist_phone': '321',
            'specialist_rank': 'error'
        }
        response = client.post('/panel/specialists/', bad_new_specialist_info)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(len(Master.objects.all()), 4)


    def test_edit_some_specialist(self):
        self.assertEqual(self.master1.name, 'Марина')
        self.assertEqual(len(self.master1.master_services_set.all()), 3)
        client = Client()
        client.login(username=self.user1.username, password='123')
        service4 = Services.objects.create(name='Стрижка бороды', master=self.master1, price=1, duration=100)
        updated_specialist_info = {
            'specialist_name': 'New master 1',
            'specialist_phone': self.master1.phone,
            'specialist_rank': self.master1.rank,
            'specialist_status': self.master1.status,
            f'service_{service4.id}': 'on'
        }
        response = client.post(f'/panel/specialists/{self.master1.id}/', updated_specialist_info)
        self.assertEqual(response.status_code, 200)
        #Перевіряємо, чи змінилося ім'я
        self.assertEqual(Master.objects.get(id=self.master1.id).name, 'New master 1')

        #Перевіряємо, чи додалися/ видалилися сервіси
        self.assertEqual(len(self.master1.master_services_set.all()), 1)

        #Перевіряємо, що поверне 500 код, якщо передати невалідні дані
        bad_update_specialist_info = {
            'specialist_name': 123,
            'specialist_phone': 321,
            'specialist_rank': 'error',
            'specialist_status': 'error',
            f'service_error': 'on'
        }
        response = client.post(f'/panel/specialists/{self.master1.id}/', bad_update_specialist_info)
        self.assertEqual(response.status_code, 500)

        # Перевіряємо, що поверне 404 код, якщо передати неіснуючий specialist_id

        response = client.post(f'/panel/specialists/555/')
        self.assertEqual(response.status_code, 404)
    def test_add_new_service(self):
        self.assertEqual(len(Services.objects.all()), 21)
        client = Client()
        client.login(username=self.user1.username, password='123')
        new_service_info = {
            'service_name': 'New Service',
            'price': 60,
            'duration': 60
        }
        response = client.post('/panel/services/', new_service_info)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Services.objects.all()), 22)

        # Перевіряємо, що поверне 500 код, якщо передати невалідні дані
        bad_service_info = {
            'service_name': 'New Service',
            'price': 'error',
            'duration': 60
        }
        response = client.post('/panel/services/', bad_service_info)
        self.assertEqual(response.status_code, 500)

    def test_edit_some_service(self):
        self.assertEqual(Services.objects.get(id=self.service1.id).name, 'Укладка волос')
        client = Client()
        client.login(username=self.user1.username, password='123')
        new_service_info = {
            'service_name': 'new name',
            'price': self.service1.price,
            'duration': self.service1.duration
        }
        response = client.post(f'/panel/services/{self.service1.id}/', new_service_info)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Services.objects.get(id=self.service1.id).name, 'new name')

        # Перевіряємо, що поверне 500 код, якщо передати невалідні дані
        bad_service_info = {
            'service_name': 'New Service',
            'price': 'error',
            'duration': 'error'
        }
        response = client.post(f'/panel/services/{self.service1.id}/', bad_service_info)
        self.assertEqual(response.status_code, 500)

        # Перевіряємо, що поверне 404 код, якщо передати неіснуючий specialist_id
        response = client.post(f'/panel/services/555/')
        self.assertEqual(response.status_code, 404)

    def test_add_schedule(self):
        self.assertEqual(len(Schedule.objects.filter(master=self.master1).all()),2)
        client = Client()
        client.login(username=self.user1.username, password='123')
        new_schedule_info = {f'date_{self.schedule1.id}': self.schedule1.date,
            f'start_time_{self.schedule1.id}' : self.schedule1.start_time,
            f'end_time_{self.schedule1.id}': self.schedule1.end_time,
            f'date_{self.schedule2.id}': self.schedule2.date,
            f'start_time_{self.schedule2.id}': self.schedule2.start_time,
            f'end_time_{self.schedule2.id}': self.schedule2.end_time,
            'new_date_0': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'new_start_time_0' : '10:00',
            'new_end_time_0': '17:00'
        }
        client.post(f'/panel/specialists/{self.master1.id}/edit_schedule', new_schedule_info)
        self.assertEqual(len(Schedule.objects.filter(master=self.master1).all()), 3)
    def test_edit_schedule(self):
        self.assertEqual(Schedule.objects.get(id= self.schedule1.id).date, date.today())
        client = Client()
        client.login(username=self.user1.username, password='123')
        editing_schedule_info = {f'date_{self.schedule1.id}': self.schedule1.date+timedelta(days=5),
                             f'start_time_{self.schedule1.id}': self.schedule1.start_time,
                             f'end_time_{self.schedule1.id}': self.schedule1.end_time}
        client.post(f'/panel/specialists/{self.master1.id}/edit_schedule', editing_schedule_info)
        self.assertEqual(Schedule.objects.get(id=self.schedule1.id).date, date.today()+timedelta(days=5))

    def test_delete_schedule(self):
        self.assertEqual(len(Schedule.objects.filter(master=self.master1).all()),2)
        client = Client()
        client.login(username=self.user1.username, password='123')
        deleting_schedule_info = {f'date_{self.schedule1.id}': self.schedule1.date,
                                 f'start_time_{self.schedule1.id}': self.schedule1.start_time,
                                 f'end_time_{self.schedule1.id}': self.schedule1.end_time}
        client.post(f'/panel/specialists/{self.master1.id}/edit_schedule', deleting_schedule_info)
        self.assertEqual(len(Schedule.objects.filter(master=self.master1).all()), 1)
