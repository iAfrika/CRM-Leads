from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_edit'),
    path('<int:pk>/update-status/', views.update_document_status, name='update_document_status'),
    path('<int:pk>/download/', views.document_download, name='document_download'),
    path('<int:pk>/generate-invoice/', views.generate_invoice_from_document, name='generate_invoice'),
    path('share/', views.share_document, name='share_document'),
    path('<int:pk>/delete/', views.delete_document, name='document_delete'),
    path('quote/new/', views.QuoteCreateView.as_view(), name='quote_create'),
    path('quote/create/', views.quote_create, name='quote_create_function'),
    path('quote/<int:pk>/', views.quote_detail, name='quote_detail'),
    path('quote/<int:quote_id>/generate-pdf/', views.generate_quote_pdf, name='generate_quote_pdf'),
    path('quote/get-number/', views.get_quote_number, name='get_quote_number'),
    path('quote/<int:quote_id>/generate-invoice/', views.generate_invoice_from_quote, name='generate_invoice_from_quote'),
    path('quote/<int:quote_id>/view/', views.view_saved_quote, name='view_saved_quote'),
    path('quote/preview/', views.quote_preview, name='quote_preview'),
    path('quote/preview/<int:quote_id>/', views.quote_preview, name='quote_preview'),
    path('quote/preview/template/', views.quote_preview_template, name='quote_preview_template'),
    path('expenditure/', views.expenditure_view, name='expenditure'),
    path('expenditure/create/', views.expenditure_create, name='expenditure_create'),
    path('expenditure/<int:pk>/edit/', views.expenditure_edit, name='expenditure_edit'),
    path('expenditure/<int:pk>/delete/', views.expenditure_delete, name='expenditure_delete'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('<int:pk>/generate-pdf/', views.generate_document_pdf, name='generate_document_pdf'),
    path('chart-data/', views.chart_data, name='chart_data'),
    path('expense-sheet/<int:pk>/', views.expense_sheet_detail, name='expense_sheet_detail'),
    path('purchase-order/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
]
