from django.urls import path
from . import views
from . import category_views
from . import supplier_views
from . import report_views

app_name = 'products'

urlpatterns = [
    # Product URLs
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('create/', views.product_create, name='product_create'),
    path('<int:pk>/update/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    
    # Category URLs
    path('categories/', category_views.category_list, name='category_list'),
    path('categories/<int:pk>/', category_views.category_detail, name='category_detail'),
    path('categories/create/', category_views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', category_views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', category_views.category_delete, name='category_delete'),
    
    # Supplier URLs
    path('suppliers/', supplier_views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', supplier_views.supplier_detail, name='supplier_detail'),
    path('suppliers/create/', supplier_views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/update/', supplier_views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', supplier_views.supplier_delete, name='supplier_delete'),
    
    # Report URLs
    path('reports/inventory/', report_views.inventory_report, name='inventory_report'),
    path('reports/purchases/', report_views.purchases_report, name='purchases_report'),
]