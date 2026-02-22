from django.urls import path
from . import views
from . import admin_views

app_name = 'access_control'

urlpatterns = [
    path('', views.manage_permissions, name='manage'),
    path('scan/', views.scan_views, name='scan'),
    path('dashboard/', views.manage_permissions, name='dashboard'),
    
    path('admin/', admin_views.admin_index, name='admin_index'),
    path('admin/views/', admin_views.admin_views, name='admin_views'),
    path('admin/views/add/', admin_views.admin_view_edit, name='admin_view_add'),
    path('admin/views/<int:pk>/', admin_views.admin_view_detail, name='admin_view_detail'),
    path('admin/views/<int:pk>/edit/', admin_views.admin_view_edit, name='admin_view_edit'),
    path('admin/views/<int:pk>/delete/', admin_views.admin_view_delete, name='admin_view_delete'),
    
    path('admin/users/', admin_views.admin_users, name='admin_users'),
    path('admin/users/<int:pk>/', admin_views.admin_user_detail, name='admin_user_detail'),
    
    path('admin/permissions/', admin_views.admin_permissions, name='admin_permissions'),
    path('admin/permissions/add/', admin_views.admin_permission_edit, name='admin_permission_add'),
    path('admin/permissions/<int:pk>/', admin_views.admin_permission_detail, name='admin_permission_detail'),
    path('admin/permissions/<int:pk>/edit/', admin_views.admin_permission_edit, name='admin_permission_edit'),
    path('admin/permissions/<int:pk>/delete/', admin_views.admin_permission_delete, name='admin_permission_delete'),
    path('admin/permissions/<int:pk>/toggle/', admin_views.admin_permission_toggle, name='admin_permission_toggle'),
] 