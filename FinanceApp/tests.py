from django.test import TestCase
from FinanceApp.models import User
from datetime import datetime

# Create your tests here.


class BaseUserModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseUserModelTestCase, cls).setUpClass()
        cls.user = User(first_name="jan", last_name="kowalski", password="asd", email="asd@asd.com")
        cls.user.save()


class UserModelTestCase(BaseUserModelTestCase):

    def test_created_properly(self):
        self.assertEqual(self.user.first_name, 'jan')

    def test_it_has_information_fields(self):
        self.assertIsInstance(self.user.first_name, str)
        self.assertIsInstance(self.user.last_name, str)

    def test_it_has_timestamps(self):
        self.assertIsInstance(self.user.date_joined, datetime)