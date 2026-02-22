from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # Purchase URLs
    path('', views.purchase_list, name='purchase_list'),
    path('create/', views.purchase_create, name='purchase_create'),
    path('<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('<int:pk>/update/', views.purchase_update, name='purchase_update'),
    path('<int:pk>/delete/', views.purchase_delete, name='purchase_delete'),
    path('<int:pk>/generate-purchase-order/', views.generate_purchase_order, name='generate_purchase_order'),
    
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Reports URL
    path('reports/', views.purchase_reports, name='purchase_reports'),
] 