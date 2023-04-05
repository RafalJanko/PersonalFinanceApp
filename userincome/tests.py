from django.test import TestCase
from userincome.models import UserIncome
from datetime import date, datetime
from django.contrib.auth.models import User

# Create your tests here.


class BaseUserIncomeModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseUserIncomeModelTestCase, cls).setUpClass()
        cls.income = UserIncome(amount=5000, description="test", date=datetime.today(), owner_id=1)
        cls.income.save()
        cls.user = User(first_name="jan", last_name="kowalski", password="asd", email="asd@asd.com")
        cls.user.save()


class UserIncomeTestCase(BaseUserIncomeModelTestCase):

    def test_created_properly(self):
        self.assertEqual(self.income.description, 'test')

    def test_it_has_information_fields(self):
        self.assertIsInstance(self.income.amount, int)
        self.assertIsInstance(self.income.description, str)

    def test_it_has_date_fields(self):
        self.assertIsInstance(self.income.date, datetime)
