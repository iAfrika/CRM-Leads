from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('', views.registration_home, name='registration_home'),
    path('register-user/', views.register_user, name='register_user'),
    path('app-selection/', views.app_selection, name='app_selection'),
    # Company selection and activation
    path('company-selection/', views.company_selection, name='company_selection'),
    path('company/<int:company_id>/activate/', views.activate_company, name='activate_company'),
    # Company related URLs
    path('companies/', views.company_list, name='company_list'),  # New dedicated list view
    path('company/details/', views.company_details, name='company_details'),  # Keep for backward compatibility
    path('company/details/<int:company_id>/', views.company_details, name='company_details'),  # New detail view with ID
    path('company/<int:company_id>/edit/', views.edit_company, name='edit_company'),
    path('register-company/', views.register_company, name='register_company'),
    # Company app management
    path('company/<int:company_id>/apps/', views.company_apps, name='company_apps'),
    # Company user management
    path('company/<int:company_id>/users/', views.company_users, name='company_users'),
    path('company/<int:company_id>/register-user/', views.register_company_user, name='register_company_user'),
    path('company/<int:company_id>/assign-user/', views.assign_existing_user, name='assign_existing_user'),
    path('company/<int:company_id>/user/<int:user_id>/edit/', views.edit_company_user, name='edit_company_user'),
    path('company/<int:company_id>/user/<int:user_id>/remove/', views.remove_company_user, name='remove_company_user'),
    # User profile management
    path('company/<int:company_id>/user/<int:user_id>/profile/', views.user_profile, name='user_profile'),
    path('company/<int:company_id>/user/<int:user_id>/profile/edit/', views.edit_user_profile, name='edit_user_profile'),
    path('users/', views.users_list, name='users_list'),
    # Add this back as placeholder to prevent NoReverseMatch errors
    path('subscription-plans/', views.placeholder_subscription_plans, name='subscription_plans'),
]