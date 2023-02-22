from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
# Create your views here.


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    return render(request, 'FinanceApp/index.html', {'categories': categories})

def add_expense(request):
    categories = Category.objects.all()
    return render(request, 'FinanceApp/add_expense.html', {'categories': categories})
