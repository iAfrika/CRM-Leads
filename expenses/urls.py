from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    # Expense URLs
    path('', views.expense_list, name='expense_list'),
    path('create/', views.expense_create, name='expense_create'),
    path('<int:pk>/', views.expense_detail, name='expense_detail'),
    path('<int:pk>/update/', views.expense_update, name='expense_update'),
    path('<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('<int:pk>/generate-expense-sheet/', views.generate_expense_sheet, name='generate_expense_sheet'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Recurring Expense URLs
    path('recurring/', views.recurring_expense_list, name='recurring_expense_list'),
    path('recurring/create/', views.recurring_expense_create, name='recurring_expense_create'),
    path('recurring/<int:pk>/update/', views.recurring_expense_update, name='recurring_expense_update'),
    path('recurring/<int:pk>/delete/', views.recurring_expense_delete, name='recurring_expense_delete'),
    path('recurring/<int:pk>/toggle/', views.recurring_expense_toggle, name='recurring_expense_toggle'),
    path('reports/', views.expense_reports, name='expense_reports'),
] 