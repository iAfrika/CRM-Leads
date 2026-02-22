from django.urls import path
from . import views

app_name = 'project_management'

urlpatterns = [
    # Project URLs
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/update/', views.project_update, name='project_update'),
    path('project/delete/', views.project_delete, name='project_delete'),
    path('project/<int:pk>/delete/', views.project_delete, name='project_delete_with_pk'),
    path('<int:pk>/finances/', views.project_finances, name='project_finances'),
    
    # Dashboard URLs
    path('dashboard/', views.project_dashboard, name='project_dashboard'),
    path('analytics/', views.project_analytics, name='project_analytics'),
    
    # Document URLs
    path('<int:project_pk>/documents/create/', views.document_create, name='document_create'),
    path('documents/<int:pk>/edit/', views.document_update, name='document_update'),
    path('<int:project_pk>/documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:pk>/download/', views.document_download, name='document_download'),
    
    # Milestone URLs
    path('<int:project_pk>/milestones/create/', views.milestone_create, name='milestone_create'),
    path('milestones/<int:pk>/edit/', views.milestone_update, name='milestone_update'),
    path('milestones/<int:pk>/delete/', views.milestone_delete, name='milestone_delete'),
    path('milestones/<int:pk>/toggle/', views.milestone_toggle, name='milestone_toggle'),
    path('milestones/<int:pk>/update-percentage/', views.milestone_update_percentage, name='milestone_update_percentage'),
    
    # Note URLs
    path('<int:project_pk>/notes/create/', views.note_create, name='note_create'),
    path('notes/<int:pk>/edit/', views.note_update, name='note_update'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('notes/<int:pk>/toggle-pin/', views.note_toggle_pin, name='note_toggle_pin'),
    
    # Finance URLs
    path('finances/create/<int:project_pk>/', views.finance_create, name='finance_create'),
    path('finances/update/<int:pk>/', views.finance_update, name='finance_update'),
    path('finances/delete/<int:pk>/', views.finance_delete, name='finance_delete'),
    path('finances/get/<int:pk>/', views.finance_get, name='finance_get'),
] 