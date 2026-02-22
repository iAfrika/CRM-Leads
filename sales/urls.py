from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('<int:pk>/', views.SaleDetailView.as_view(), name='sale_detail'),
    path('create/', views.SaleCreateView.as_view(), name='sale_create'),
    path('<int:pk>/edit/', views.SaleUpdateView.as_view(), name='sale_update'),
    path('<int:pk>/delete/', views.SaleDeleteView.as_view(), name='sale_delete'),
    path('direct-sale/', views.direct_sale_form, name='direct_sale_form'),
    path('direct-sale/create/', views.direct_sale_create, name='direct_sale_create'),
    path('<int:pk>/generate-receipt/', views.generate_receipt, name='generate_receipt'),
    path('<int:pk>/preview-receipt/', views.preview_receipt, name='preview_receipt'),
    path('<int:pk>/generate-receipt-pdf/', views.generate_receipt, name='generate_receipt_pdf'),
]