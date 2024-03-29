from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path("", views.index, name="expenses"),
    path("add-expense", views.add_expense, name="add-expenses"),
    path("edit-expense/<int:id>", views.expense_edit, name="expense-edit"),
    path("expense-delete/<int:id>", views.delete_expense, name="expense-delete"),
    path("search-expenses", csrf_exempt(views.search_expenses), name="search-expenses"),
    path(
        "expense_category_summary",
        views.expense_category_summary,
        name="expense_category_summary",
    ),
    path(
        "income_source_summary",
        views.income_source_summary,
        name="income_source_summary",
    ),
    path("stats", views.stats_view, name="stats"),
    path("income_stats", views.income_stats_view, name="income_stats"),
    path("export_csv", views.export_csv, name="export-csv"),
    path("export_excel", views.export_excel, name="export-excel"),
    path("export_pdf", views.export_pdf, name="export-pdf"),
]
