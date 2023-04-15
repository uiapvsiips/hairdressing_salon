from django.db import transaction
from django.test import TestCase, Client

from salon.models import Master, Services


class TetsAdminPanel(TestCase):
    def setUp(self):
        self.master1 = Master.objects.create(name='Master 1', phone='123', rank=2)

        self.service1 = Services.objects.create(name='Укладка волос', price=1, duration=60)
        self.service2 = Services.objects.create(name='Окрашивание волос', price=1, duration=120)
        self.service3 = Services.objects.create(name='Мужская стрижка', price=1, duration=180)

        self.master1.services.set([self.service1, self.service2, self.service3])

    def test_add_new_specialist(self):
        self.assertEqual(len(Master.objects.all()), 1)
        client = Client()
        new_specialist_info = {
            'specialist_name': 'Master 2',
            'specialist_phone': '321',
            'specialist_rank': 1
        }
        response = client.post('/panel/specialists/', new_specialist_info)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Master.objects.all()), 2)

        # Перевіряємо, що поверне 500 код, якщо передати невалідні дані
        bad_new_specialist_info = {
            'specialist_name': 'Master 2',
            'specialist_phone': '321',
            'specialist_rank': 'error'
        }
        response = client.post('/panel/specialists/', bad_new_specialist_info)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(len(Master.objects.all()), 2)


    def test_edit_some_specialist(self):
        self.assertEqual(self.master1.name, 'Master 1')
        self.assertEqual(len(self.master1.master_services_set.all()), 3)
        client = Client()
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
        self.assertEqual(Master.objects.get().name, 'New master 1')

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
        self.assertEqual(len(Services.objects.all()), 3)
        client = Client()
        new_service_info = {
            'service_name': 'New Service',
            'price': 60,
            'duration': 60
        }
        response = client.post('/panel/services/', new_service_info)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Services.objects.all()), 4)

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
