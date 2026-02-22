from django.urls import path
from .views import (
    MainDashboardView, 
    MonthlyRevenueExpensesView,
    MonthlyPurchasesSalesView,
    MonthlyFinancialTrendsView
)

app_name = 'dashboard'

urlpatterns = [
    path('', MainDashboardView.as_view(), name='main_dashboard'),
    path('monthly-revenue-expenses/', MonthlyRevenueExpensesView.as_view(), name='monthly_revenue_expenses'),
    path('monthly-purchases-sales/', MonthlyPurchasesSalesView.as_view(), name='monthly_purchases_sales'),
    path('monthly-financial-trends/', MonthlyFinancialTrendsView.as_view(), name='monthly_financial_trends'),
]
