from django.urls import path
from . import views
from .views import (
    ClientListView, 
    ClientCreateView,
    ClientDetailView,  # Import the detail view class
    ClientUpdateView,
    ClientDeleteView  # Import any other view classes needed
)

app_name = 'clients'

urlpatterns = [
    path('', ClientListView.as_view(), name='client_list'),  # Use as_view() for class-based view
    path('create/', ClientCreateView.as_view(), name='client_create'),  # Use as_view() for class-based view
    path('<int:pk>/', ClientDetailView.as_view(), name='client_detail'),  # Use class-based view
    path('<int:pk>/update/', ClientUpdateView.as_view(), name='client_update'),
    path('<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
]