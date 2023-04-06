from django.test import TestCase
from FinanceApp.models import User, Expense, Category
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


class BaseExpenseModelTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseExpenseModelTestCase, cls).setUpClass()
        cls.expense = Expense(amount=5000, description="test", date=datetime.today(), owner_id=1)
        cls.expense.save()
        cls.user = User(first_name="jan", last_name="kowalski", password="asd", email="asd@asd.com")
        cls.user.save()


class UserIncomeTestCase(BaseExpenseModelTestCase):

    def test_created_properly(self):
        self.assertEqual(self.expense.description, 'test')

    def test_it_has_information_fields(self):
        self.assertIsInstance(self.expense.amount, int)
        self.assertIsInstance(self.expense.description, str)

    def test_it_has_date_fields(self):
        self.assertIsInstance(self.expense.date, datetime)
