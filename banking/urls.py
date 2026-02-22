from django.urls import path
from . import views

app_name = 'banking'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('account/create/', views.create_account, name='create_account'),
    path('account/<str:account_number>/', views.account_detail, name='account_detail'),
    path('account/<str:account_number>/deposit/', views.deposit, name='deposit'),
    path('account/<str:account_number>/withdraw/', views.withdraw, name='withdraw'),
    path('account/<str:account_number>/transfer/', views.transfer, name='transfer'),
    path('account/<str:account_number>/payment/', views.payment, name='payment'),

    path('transactions/', views.transaction_history, name='all_transactions'),
    path('account/<str:account_number>/transactions/', views.transaction_history, name='account_transactions'),
] 