# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Report list
    path('list/', views.report_list, name='report_list'),
    
    # Report types
    path('banking/', views.banking_reports, name='banking_reports'),
    path('sales/', views.sales_reports, name='sales_reports'),
    path('clients/', views.client_reports, name='clients_reports'),
    path('expenses/', views.expenses_reports, name='expenses_reports'),
    path('purchases/', views.purchases_reports, name='purchases_reports'),
    path('leads/', views.leads_reports, name='leads'),
    path('projects/', views.projects_reports, name='projects'),
    
    # Report management
    path('view/<int:report_id>/', views.view_report, name='view_report'),
    path('create/', views.create_report, name='create_report'),
    path('create_report_config/', views.create_report_config, name='create_report_config'),
    path('update/<int:report_id>/', views.update_report, name='update_report'),
    path('delete/<int:report_id>/', views.delete_report, name='delete_report'),
    path('toggle-favorite/<int:report_id>/', views.toggle_favorite, name='toggle_favorite'),
    
    # Scheduled reports
    path('scheduled/', views.scheduled_reports, name='scheduled_reports'),
    path('scheduled/create/', views.create_schedule, name='create_schedule'),
    path('scheduled/update/<int:schedule_id>/', views.update_schedule, name='update_schedule'),
    path('scheduled/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('scheduled/toggle/<int:schedule_id>/', views.toggle_schedule, name='toggle_schedule'),
    path('scheduled/resend/<int:delivery_id>/', views.resend_report, name='resend_report'),
    
    # Export
    path('export/<int:report_id>/pdf/', views.export_report_pdf, name='export_report_pdf'),
    path('export/<int:report_id>/excel/', views.export_report_excel, name='export_report_excel'),
    path('export/<int:report_id>/csv/', views.export_report_csv, name='export_report_csv'),
    
    # Analytics
    path('analytics/', views.analytics, name='analytics'),
    
    # Settings
    path('settings/', views.settings, name='settings'),
    
    # API endpoints
    path('api/reports/', views.api_get_reports, name='api_get_reports'),
    path('api/reports/<int:report_id>/', views.api_get_report, name='api_get_report'),
    path('api/reports/<int:report_id>/data/', views.api_get_report_data, name='api_get_report_data'),
    
    # Chart data endpoints
    path('api/quotes-invoices-chart/', views.get_quotes_invoices_chart, name='quotes_invoices_chart'),
    
    # Diagnostic endpoints
    path('api/diagnose-documents-chart/', views.diagnose_documents_chart_data, name='diagnose_documents_chart'),
]