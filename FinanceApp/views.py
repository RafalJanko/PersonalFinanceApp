import csv
import datetime
import json
import os
import tempfile

import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from weasyprint import HTML

from userpreferences.models import UserPreference

from .models import Category, Expense
from userincome.models import UserIncome

os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
# Create your views here.


"""
Ajax search option to look through the expenses of a logged in user
"""


def search_expenses(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get("searchText")
        expenses = (
            Expense.objects.filter(amount__istartswith=search_str, owner=request.user)
            | Expense.objects.filter(date__istartswith=search_str, owner=request.user)
            | Expense.objects.filter(
                description__icontains=search_str, owner=request.user
            )
            | Expense.objects.filter(category__icontains=search_str, owner=request.user)
        )
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


"""
The "main" page that lists all expenses and allows you to add and edit expenses.
"""


@login_required(login_url="/authentication/login")
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 6)
    page_number = request.GET.get("page")
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        "categories": categories,
        "expenses": expenses,
        "page_obj": page_obj,
        "currency": currency,
    }

    return render(request, "FinanceApp/index.html", context)


"""
The view that allows a logged in user to add an expense.
"""


def add_expense(request):
    categories = Category.objects.all()
    context = {"categories": categories, "values": request.POST}
    categories = Category.objects.all()
    if request.method == "GET":
        return render(request, "FinanceApp/add_expense.html", context)

    if request.method == "POST":
        amount = request.POST["amount"]
        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "FinanceApp/add_expense.html", context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "FinanceApp/add_expense.html", context)

        Expense.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            category=category,
            description=description,
        )
        messages.success(request, "Expense saved successfully")
        return redirect("expenses")


"""
The view that allows a logged in user to edit an expense.
"""


def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = {"expense": expense, "values": expense, "categories": categories}
    if request.method == "GET":
        return render(request, "FinanceApp/edit_expense.html", context)
    if request.method == "POST":
        amount = request.POST["amount"]
        if not amount:
            messages.error(request, "Amount is required")
            return render(request, "FinanceApp/edit_expense.html", context)

        description = request.POST["description"]
        date = request.POST["expense_date"]
        category = request.POST["category"]

        if not description:
            messages.error(request, "Description is required")
            return render(request, "FinanceApp/edit_expense.html", context)

        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()
        messages.success(request, "Expense updated successfully")
        return redirect("expenses")


"""
The view that allows a logged in user to delete an expense.
"""


def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense removed successfully!")
    return redirect("expenses")


"""
View to group expenses and count their total amount.
"""


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(
        owner=request.user, date__gte=six_months_ago, date__lte=todays_date
    )
    final_rep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            final_rep[y] = get_expense_category_amount(y)

    return JsonResponse({"expense_category_data": final_rep}, safe=False)


"""
The view that allows to view a graph summarize the expenses with a js graph.
"""


def stats_view(request):
    return render(request, "FinanceApp/stats.html")


"""
View to group incomes and count their total amount.
"""


def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    incomes = UserIncome.objects.filter(
        owner=request.user, date__gte=six_months_ago, date__lte=todays_date
    )
    final_rep = {}

    def get_source(income):
        return income.source

    category_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_category = incomes.filter(source=source)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in incomes:
        for y in category_list:
            final_rep[y] = get_income_source_amount(y)

    return JsonResponse({"income_source_data": final_rep}, safe=False)


"""
The view that allows to view a graph summarize the incomes with a js graph.
"""


def income_stats_view(request):
    return render(request, "FinanceApp/income stats.html")


"""
The view that allows a logged user to export the expenses to a CSV.
"""


def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=Expenses" + str(datetime.datetime.now()) + ".csv"
    )

    writer = csv.writer(response)
    writer.writerow(["Amount", "Description", "Category", "Date"])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow(
            [expense.amount, expense.description, expense.category, expense.date]
        )

    return response


"""
The view that allows a logged user to export the expenses to an Excel file.
"""


def export_excel(request):
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = (
        "attachment; filename=Expenses" + str(datetime.datetime.now()) + ".xls"
    )

    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Expenses")
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ["Amount", "Description", "Category", "Date"]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list(
        "amount", "description", "category", "date"
    )
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)
    return response


"""
The view that allows a logged user to export the expenses to a PDF.
"""


def export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        "inline; attachment; filename=Expenses" + str(datetime.datetime.now()) + ".pdf"
    )
    response["Content-Transfer-Encoding"] = "binary"
    expenses = Expense.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum("amount"))
    html_string = render_to_string(
        "FinanceApp/pdf-output.html",
        {"expenses": expenses, "total": sum["amount__sum"]},
    )
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, "r")
        response.write(output.read())

    return response
