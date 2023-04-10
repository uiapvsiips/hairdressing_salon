from django.test import TestCase
from salon.schedule_worker import __get_info_for_calc, calc_breaks
from django.test import TestCase
from datetime import datetime, timedelta, time, date
from salon.models import Booking


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
        new_booking = Booking(date=datetime.now().date(), start_time=new_booking_start_time.time(), end_time=new_booking_end_time.time())
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
        bookings_list = [Booking(date= datetime(2023, 4, 10), start_time= time(10, 0), end_time= time(11, 0))]

        expected_result = [
            {'start_time': self.master_start_time, 'end_time': datetime(2023, 4, 10, 10, 0) - timedelta(minutes=self.service_duration)},
            {'start_time': datetime(2023, 4, 10, 11, 0), 'end_time': self.master_end_time - timedelta(minutes=self.service_duration)}]

        result = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, bookings_list)

        self.assertEqual(result, expected_result)

    def test_multiple_bookings(self):
        bookings_list = [Booking(date=date(2023, 4, 10), start_time=time(10, 0), end_time= time(11, 0)),
                         Booking(date=date(2023, 4, 10), start_time= time(13, 0), end_time=  time(14, 0))]
        expected_result = [
            {'start_time': self.master_start_time, 'end_time': datetime(2023, 4, 10, 10, 0) - timedelta(minutes=self.service_duration)},
            {'start_time': datetime(2023, 4, 10, 11, 0),
             'end_time': datetime(2023, 4, 10, 13, 0) - timedelta(minutes=self.service_duration)},
            {'start_time': datetime(2023, 4, 10, 14, 0),
             'end_time': self.master_end_time - timedelta(minutes=self.service_duration)}]

        result = calc_breaks(self.master_start_time, self.master_end_time, self.service_duration, bookings_list)

        self.assertEqual(result, expected_result)