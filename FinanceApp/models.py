from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

# Create your models here.

""" 
Expense model related to User.
Returning respresentation in the form of a str.
Ordered by the newest date.
"""

class Expense(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=256)

    def __str__(self):
        return self.category

    class Meta:
        ordering: ["-date"]


"""
Category model.
Verbose - changes it's plural form in the Django admin page.
"""


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
