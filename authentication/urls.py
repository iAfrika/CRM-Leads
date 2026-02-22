from django.urls import path
from . import views
from . import views_staff

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile-selection/', views.profile_selection, name='profile_selection'),
    path('profile-select/<int:pk>/', views.profile_select, name='profile_select'),
    path('profile-create/', views.profile_create, name='profile_create'),
    path('password/change/', views.password_change, name='password_change'),
    path('password/reset/', views.password_reset, name='password_reset'),
    path('staff-workspace/', views_staff.staff_workspace, name='staff_workspace'),
]