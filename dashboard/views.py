from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.db.models import (
    Sum, 
    Q, 
    F, 
    Value, 
    ExpressionWrapper, 
    DurationField, 
    Count, 
    Avg
)
from purchases.models import Purchase
from sales.models import Sale
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from datetime import timedelta
from decimal import Decimal
import json
import logging
from documents.models import Document
from banking.models import Transaction
from leads.models import Lead
from projects.models import Project, JobCard

def debug_document_date_range():
    """Helper function to print document date range debugging information."""
    all_documents = Document.objects.all()
    now = timezone.now()
    twelve_months_ago = now - timezone.timedelta(days=365)

    print("\n--- DATE RANGE DEBUGGING ---")
    print(f"Current Date: {now}")
    print(f"12 Months Ago: {twelve_months_ago}")
    print(f"Date Range: {twelve_months_ago} to {now}")

    # Find the earliest and latest documents
    earliest_doc = all_documents.order_by('created_at').first()
    latest_doc = all_documents.order_by('-created_at').first()
    
    print("\nDocument Date Range:")
    if earliest_doc:
        print(f"Earliest Document: {earliest_doc.created_at}")
    if latest_doc:
        print(f"Latest Document: {latest_doc.created_at}")
    
    # Print document type distribution
    document_type_counts = all_documents.values('document_type').annotate(count=Count('id'))
    print("\nDocument Type Distribution:")
    for doc_type in document_type_counts:
        print(f"{doc_type['document_type']}: {doc_type['count']} documents")
    
    print("--- END OF DATE RANGE DEBUGGING ---\n")

    return twelve_months_ago

class MainDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/main_dashboard.html'

    def get_recent_pending_quotes(self):
        """
        Fetch recent pending quotes with live data.
        Includes more detailed filtering and sorting.
        """
        today = timezone.now().date()
        return Document.objects.filter(
            Q(document_type='QUOTE') & 
            (Q(status='DRAFT') | Q(status='SENT')) &
            Q(created_at__gte=today - timedelta(days=30))
        ).select_related('client').annotate(
            days_pending=ExpressionWrapper(
                today - F('created_at__date'), 
                output_field=DurationField()
            ),
            client_name=F('client__name')
        ).order_by('-created_at')[:5]

    def get_recent_overdue_invoices(self):
        """
        Fetch recent overdue invoices with live data.
        Includes more comprehensive overdue calculation.
        """
        today = timezone.now().date()
        return Document.objects.filter(
            document_type='INVOICE',
            status__in=['SENT', 'OVERDUE'],
            due_date__lt=today
        ).select_related('client').annotate(
            days_overdue=ExpressionWrapper(
                today - F('due_date'), 
                output_field=DurationField()
            ),
            client_name=F('client__name')
        ).order_by('due_date')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate quotes and invoices metrics
        quotes = Document.objects.filter(document_type='QUOTE')
        invoices = Document.objects.filter(document_type='INVOICE')

        # Count of quotes and invoices
        quotes_count = quotes.count()
        invoices_count = invoices.count()

        # Total value of quotes and invoices
        quotes_total_value = quotes.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        invoices_total_value = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # Average amount per document
        quotes_avg_amount = quotes.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')
        invoices_avg_amount = invoices.aggregate(avg=Avg('total_amount'))['avg'] or Decimal('0.00')

        # Calculate total amount based on count and average
        quotes_total_amount = quotes_count * quotes_avg_amount
        invoices_total_amount = invoices_count * invoices_avg_amount

        # Get current month's data
        current_month = timezone.now().month
        current_year = timezone.now().year

        # Monthly quotes and invoices
        monthly_quotes = quotes.filter(
            created_at__month=current_month, 
            created_at__year=current_year
        )
        monthly_invoices = invoices.filter(
            created_at__month=current_month, 
            created_at__year=current_year
        )

        # Monthly metrics
        monthly_quotes_count = monthly_quotes.count()
        monthly_invoices_count = monthly_invoices.count()
        monthly_quotes_value = monthly_quotes.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        monthly_invoices_value = monthly_invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # Existing chart data
        quotes_invoices = {
            'labels': ['Quotes', 'Invoices'],
            'datasets': [{
                'label': 'Quotes vs Invoices',
                'data': [quotes_count, invoices_count],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.7)',   # Blue for Quotes
                    'rgba(255, 99, 132, 0.7)'    # Red for Invoices
                ]
            }]
        }
        context['quotes_invoices_data'] = mark_safe(json.dumps(quotes_invoices))

        # Existing revenue and expenditure chart data
        revenue_expenditure = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr'],
            'datasets': [
                {
                    'label': 'Revenue',
                    'data': [65000, 59000, 80000, 81000],
                    'backgroundColor': 'rgba(75, 192, 192, 0.7)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Expenditure',
                    'data': [28000, 48000, 40000, 19000],
                    'backgroundColor': 'rgba(255, 99, 132, 0.7)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        }
        context['revenue_expenditure_data'] = mark_safe(json.dumps(revenue_expenditure))

        # Existing purchases vs sales chart data
        purchases_sales = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr'],
            'datasets': [
                {
                    'label': 'Sales',
                    'data': [12000, 19000, 15000, 22000],
                    'backgroundColor': 'rgba(54, 162, 235, 0.7)'
                },
                {
                    'label': 'Purchases',
                    'data': [9000, 14000, 11000, 17000],
                    'backgroundColor': 'rgba(255, 206, 86, 0.7)'
                }
            ]
        }
        context['purchases_sales_data'] = mark_safe(json.dumps(purchases_sales))

        # Existing monthly financial trends chart data
        monthly_trends = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [
                {
                    'label': 'Total Revenue',
                    'data': [65000, 59000, 80000, 81000, 56000],
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.3,
                    'fill': True
                },
                {
                    'label': 'Total Expenses',
                    'data': [28000, 48000, 40000, 19000, 35000],
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.3,
                    'fill': True
                }
            ]
        }
        context['monthly_trends_data'] = mark_safe(json.dumps(monthly_trends))

        # Add monthly trends data
        monthly_trends_data = {
            'labels': ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
            'revenue': [0] * 12,
            'expenses': [0] * 12,
            'purchases': [0] * 12,
            'quotes': [0] * 12,
            'net_profit': [0] * 12
        }
        
        # Fetch actual financial data
        now = timezone.now()
        twelve_months_ago = now - timezone.timedelta(days=365)

        # Revenue
        revenue_data = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='INVOICE'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')

        for entry in revenue_data:
            month_index = entry['month'].month - 1
            monthly_trends_data['revenue'][month_index] = float(entry['total'])

        # Expenses
        expenses_data = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='EXPENSE'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')

        for entry in expenses_data:
            month_index = entry['month'].month - 1
            monthly_trends_data['expenses'][month_index] = float(entry['total'])

        # Purchases
        purchases_data = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='PURCHASE'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')

        logging.info("Purchases data: %s", purchases_data.query)

        for entry in purchases_data:
            month_index = entry['month'].month - 1
            monthly_trends_data['purchases'][month_index] = float(entry['total'])

        # Quotes
        quotes_data = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='QUOTE'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total=Sum('total_amount')
        ).order_by('month')

        for entry in quotes_data:
            month_index = entry['month'].month - 1
            monthly_trends_data['quotes'][month_index] = float(entry['total'])

        # Net Profit
        for i in range(12):
            monthly_trends_data['net_profit'][i] = (
                monthly_trends_data['revenue'][i] - 
                monthly_trends_data['expenses'][i] - 
                monthly_trends_data['purchases'][i]
            )

        # Convert to JSON string for template
        context['monthly_trends_data'] = json.dumps(monthly_trends_data)

        # Calculate total revenue, expenses, and PNL
        total_revenue = invoices_total_value
        total_expenses = Transaction.objects.filter(
            transaction_type='EXPENSE'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        pnl_value = total_revenue - total_expenses
        
        last_month = timezone.now().replace(day=1) - timezone.timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        
        last_month_invoices = invoices.filter(
            created_at__gte=last_month_start,
            created_at__lte=last_month
        )
        last_month_total_revenue = last_month_invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        last_month_transactions = Transaction.objects.filter(
            transaction_type='EXPENSE',
            timestamp__gte=last_month_start,
            timestamp__lte=last_month
        )
        last_month_total_expenses = last_month_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        revenue_change = (
            ((total_revenue - last_month_total_revenue) / last_month_total_revenue * 100) 
            if last_month_total_revenue > 0 else 0
        )
        
        expenses_change = (
            ((total_expenses - last_month_total_expenses) / last_month_total_expenses * 100) 
            if last_month_total_expenses > 0 else 0
        )
        
        last_month_pnl = last_month_total_revenue - last_month_total_expenses
        pnl_change = (
            ((pnl_value - last_month_pnl) / abs(last_month_pnl) * 100) 
            if last_month_pnl != 0 else 0
        )

        # Calculate Purchases Metrics
        total_purchases = Purchase.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        last_month_purchases = Purchase.objects.filter(
            date__gte=last_month_start,
            date__lte=last_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        purchases_change = (
            ((total_purchases - last_month_purchases) / last_month_purchases * 100) 
            if last_month_purchases > 0 else 0
        )

        # Calculate Sales Metrics
        total_sales = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        last_month_sales = Sale.objects.filter(
            sale_date__gte=last_month_start,
            sale_date__lte=last_month
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        sales_change = (
            ((total_sales - last_month_sales) / last_month_sales * 100) 
            if last_month_sales > 0 else 0
        )

        # Fetch live pending quotes data
        recent_pending_quotes = self.get_recent_pending_quotes()
        context['recent_pending_quotes'] = recent_pending_quotes
        context['total_pending_quotes'] = recent_pending_quotes.count()
        context['total_pending_quotes_value'] = recent_pending_quotes.aggregate(
            total=Coalesce(Sum('total_amount'), Value(Decimal('0.00')))
        )['total']

        # Fetch live overdue invoices data
        recent_overdue_invoices = self.get_recent_overdue_invoices()
        context['recent_overdue_invoices'] = recent_overdue_invoices
        context['total_overdue_invoices'] = recent_overdue_invoices.count()
        context['total_overdue_invoices_value'] = recent_overdue_invoices.aggregate(
            total=Coalesce(Sum('total_amount'), Value(Decimal('0.00')))
        )['total']

        # Calculate total revenue, expenses, and PNL
        total_revenue = invoices_total_value
        total_expenses = Transaction.objects.filter(
            transaction_type='EXPENSE'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        pnl_value = total_revenue - total_expenses
        
        last_month = timezone.now().replace(day=1) - timezone.timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        
        last_month_invoices = invoices.filter(
            created_at__gte=last_month_start,
            created_at__lte=last_month
        )
        last_month_total_revenue = last_month_invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        last_month_transactions = Transaction.objects.filter(
            transaction_type='EXPENSE',
            timestamp__gte=last_month_start,
            timestamp__lte=last_month
        )
        last_month_total_expenses = last_month_transactions.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        revenue_change = (
            ((total_revenue - last_month_total_revenue) / last_month_total_revenue * 100) 
            if last_month_total_revenue > 0 else 0
        )
        
        expenses_change = (
            ((total_expenses - last_month_total_expenses) / last_month_total_expenses * 100) 
            if last_month_total_expenses > 0 else 0
        )
        
        last_month_pnl = last_month_total_revenue - last_month_total_expenses
        pnl_change = (
            ((pnl_value - last_month_pnl) / abs(last_month_pnl) * 100) 
            if last_month_pnl != 0 else 0
        )

        # Prepare analytics overview data
        now = timezone.now()
        twelve_months_ago = now - timezone.timedelta(days=365)

        # Monthly Revenue Breakdown
        monthly_revenue = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='INVOICE',
            status='PAID'
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_revenue=Sum('total_amount')
        ).order_by('month')

        # Monthly Lead Conversion
        monthly_leads = Lead.objects.filter(
            created_at__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            total_leads=Count('id'),
            converted_leads=Count('id', filter=Q(status='CONVERTED'))
        ).order_by('month')

        # Project Status Distribution
        project_status_counts = JobCard.objects.values('status').annotate(
            total_projects=Count('project', distinct=True)
        )

        # Prepare data for Chart.js
        # Monthly Revenue Chart
        monthly_revenue_labels = [
            month['month'].strftime('%b %Y') for month in monthly_revenue
        ]
        monthly_revenue_data = [
            float(month['total_revenue']) for month in monthly_revenue
        ]

        # Lead Conversion Chart
        lead_conversion_labels = [
            month['month'].strftime('%b %Y') for month in monthly_leads
        ]
        lead_conversion_data = {
            'total_leads': [month['total_leads'] for month in monthly_leads],
            'converted_leads': [month['converted_leads'] for month in monthly_leads]
        }

        # Project Status Chart
        project_status_labels = [
            status['status'] for status in project_status_counts
        ]
        project_status_data = [
            status['total_projects'] for status in project_status_counts
        ]

        # Add to context for use in templates
        context.update({
            # Monthly Revenue Analytics
            'monthly_revenue_labels': mark_safe(json.dumps(monthly_revenue_labels)),
            'monthly_revenue_data': mark_safe(json.dumps(monthly_revenue_data)),

            # Lead Conversion Analytics
            'lead_conversion_labels': mark_safe(json.dumps(lead_conversion_labels)),
            'lead_conversion_data': mark_safe(json.dumps(lead_conversion_data)),

            # Project Status Analytics
            'project_status_labels': mark_safe(json.dumps(project_status_labels)),
            'project_status_data': mark_safe(json.dumps(project_status_data)),
        })

        # Prepare context data
        context.update({
            # Overall document metrics
            'quotes_count': quotes_count,
            'invoices_count': invoices_count,
            'quotes_total_value': quotes_total_value,
            'invoices_total_value': invoices_total_value,
            'quotes_avg_amount': quotes_avg_amount,
            'invoices_avg_amount': invoices_avg_amount,
            'quotes_total_amount': quotes_total_amount,
            'invoices_total_amount': invoices_total_amount,

            # Current month metrics
            'monthly_quotes_count': monthly_quotes_count,
            'monthly_invoices_count': monthly_invoices_count,
            'monthly_quotes_value': monthly_quotes_value,
            'monthly_invoices_value': monthly_invoices_value,

            # Additional context for dashboard visualization
            'total_documents': quotes_count + invoices_count,
            'total_document_value': quotes_total_value + invoices_total_value,

            # Total revenue, expenses, and PNL
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'pnl_value': pnl_value,
            'revenue_change': revenue_change,
            'expenses_change': expenses_change,
            'pnl_change': pnl_change,

            # Purchases metrics
            'total_purchases': total_purchases,
            'purchases_change': purchases_change,

            # Sales metrics
            'total_sales': total_sales,
            'sales_change': sales_change,

            # Pending Quotes metrics
            'total_pending_quotes': recent_pending_quotes.count(),
            'total_pending_quotes_value': recent_pending_quotes.aggregate(
                total=Coalesce(Sum('total_amount'), Value(Decimal('0.00')))
            )['total'],

            # Overdue Invoices metrics
            'total_overdue_invoices': recent_overdue_invoices.count(),
            'total_overdue_invoices_value': recent_overdue_invoices.aggregate(
               total=Coalesce(Sum('total_amount'), Value(Decimal('0.00')))
            )['total'],
        })

        return context

class MonthlyRevenueExpensesView(View):
    def get(self, request, *args, **kwargs):
        # Get the current date
        now = timezone.now()
        
        # Calculate the start of the 12-month period
        twelve_months_ago = now - timezone.timedelta(days=365)

        # Prepare month labels starting from January of the current year
        current_year = now.year
        month_labels = [
            timezone.datetime(current_year, month, 1).strftime('%b') 
            for month in range(1, 13)
        ]

        # Calculate Revenue
        # 1. Paid Invoices
        paid_invoices = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='INVOICE',
            status='PAID'
        ).annotate(
            month=TruncMonth('created_at')
        )

        # 2. Quotes (assuming these are sales documents)
        quotes = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='QUOTE'
        ).annotate(
            month=TruncMonth('created_at')
        )

        # Calculate Expenses
        # 1. Expense Sheets
        expense_sheets = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='EXPENSE_SHEET'
        ).annotate(
            month=TruncMonth('created_at')
        )

        # 2. Purchase Orders
        purchase_orders = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type='PURCHASE_ORDER'
        ).annotate(
            month=TruncMonth('created_at')
        )

        # Debug print for all revenue sources
        print("\n--- Revenue Sources Debug ---")
        print("Paid Invoices:")
        for inv in paid_invoices:
            print(f"ID: {inv.id}, Date: {inv.created_at}, Month: {inv.created_at.strftime('%b')}, Total: {inv.total_amount}")
        
        print("\nQuotes:")
        for quote in quotes:
            print(f"Sales Doc ID: {quote.id}, Date: {quote.created_at}, Month: {quote.created_at.strftime('%b')}, Total: {quote.total_amount}")

        # Debug print for expense sources
        print("\n--- Expense Sources Debug ---")
        print("Expense Sheets:")
        for expense in expense_sheets:
            print(f"ID: {expense.id}, Date: {expense.created_at}, Month: {expense.created_at.strftime('%b')}, Total: {expense.total_amount}")
        
        print("\nPurchase Orders:")
        for po in purchase_orders:
            print(f"ID: {po.id}, Date: {po.created_at}, Month: {po.created_at.strftime('%b')}, Total: {po.total_amount}")

        # Initialize data arrays
        revenue_data = [0] * 12
        expenses_data = [0] * 12

        # Aggregate Revenue by Month
        revenue_by_month = {}
        for doc in list(paid_invoices) + list(quotes):
            month = doc.created_at.strftime('%b')
            if month not in revenue_by_month:
                revenue_by_month[month] = 0
            revenue_by_month[month] += float(doc.total_amount)

        # Aggregate Expenses by Month
        expenses_by_month = {}
        for doc in list(expense_sheets) + list(purchase_orders):
            month = doc.created_at.strftime('%b')
            if month not in expenses_by_month:
                expenses_by_month[month] = 0
            expenses_by_month[month] += float(doc.total_amount)

        # Map to data arrays
        for i, month in enumerate(month_labels):
            revenue_data[i] = revenue_by_month.get(month, 0)
            expenses_data[i] = expenses_by_month.get(month, 0)

        # Prepare response
        response_data = {
            'labels': month_labels,
            'revenue': revenue_data,
            'expenses': expenses_data
        }

        # Debug print
        print("\n--- Revenue vs Expenses Data ---")
        print(f"Labels: {response_data['labels']}")
        print(f"Revenue: {response_data['revenue']}")
        print(f"Expenses: {response_data['expenses']}")

        return JsonResponse(response_data)

class MonthlyPurchasesSalesView(View):
    def get(self, request, *args, **kwargs):
        # Get the current date
        now = timezone.now()
        
        # Calculate the start of the 12-month period
        twelve_months_ago = now - timezone.timedelta(days=365)

        # Prepare month labels starting from January of the current year
        current_year = now.year
        month_labels = [
            timezone.datetime(current_year, month, 1).strftime('%b') 
            for month in range(1, 13)
        ]

        # Get sales documents (Invoices and Quotes)
        sales_docs = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type__in=['INVOICE', 'QUOTE']
        )

        # Get purchase documents
        purchase_docs = Document.objects.filter(
            created_at__gte=twelve_months_ago,
            document_type__in=['PURCHASE_ORDER', 'PURCHASE']
        )

        # Debug print for sales documents
        print("\n--- Sales Documents Debug ---")
        for doc in sales_docs:
            print(f"Sales Doc ID: {doc.id}, Date: {doc.created_at}, Month: {doc.created_at.strftime('%b')}, Total: {doc.total_amount}")

        # Debug print for purchase documents
        print("\n--- Purchase Documents Debug ---")
        for doc in purchase_docs:
            print(f"Purchase Doc ID: {doc.id}, Date: {doc.created_at}, Month: {doc.created_at.strftime('%b')}, Total: {doc.total_amount}")

        # Aggregate Sales by Month
        sales_by_month = {}
        for doc in sales_docs:
            month = doc.created_at.strftime('%b')
            if month not in sales_by_month:
                sales_by_month[month] = 0
            sales_by_month[month] += float(doc.total_amount)

        # Aggregate Purchases by Month
        purchases_by_month = {}
        for doc in purchase_docs:
            month = doc.created_at.strftime('%b')
            if month not in purchases_by_month:
                purchases_by_month[month] = 0
            purchases_by_month[month] += float(doc.total_amount)

        # Initialize data arrays
        sales_data = [0] * 12
        purchases_data = [0] * 12

        # Map to data arrays
        for i, month in enumerate(month_labels):
            sales_data[i] = sales_by_month.get(month, 0)
            purchases_data[i] = purchases_by_month.get(month, 0)

        # Prepare response
        response_data = {
            'labels': month_labels,
            'sales': sales_data,
            'purchases': purchases_data
        }

        # Debug print
        print("\n--- Purchases vs Sales Data ---")
        print(f"Labels: {response_data['labels']}")
        print(f"Sales: {response_data['sales']}")
        print(f"Purchases: {response_data['purchases']}")

        return JsonResponse(response_data)

class MonthlyFinancialTrendsView(View):
    def get(self, request, *args, **kwargs):
        # Get the current date
        now = timezone.now()
        
        # Calculate the start of the 12-month period
        twelve_months_ago = now - timezone.timedelta(days=365)

        # Prepare month labels starting from January of the current year
        current_year = now.year
        month_labels = [
            timezone.datetime(current_year, month, 1).strftime('%b') 
            for month in range(1, 13)
        ]

        # Comprehensive financial metrics
        metrics_docs = {
            'revenue': Document.objects.filter(
                created_at__gte=twelve_months_ago,
                document_type__in=['INVOICE', 'QUOTE']
            ),
            'expenses': Document.objects.filter(
                created_at__gte=twelve_months_ago,
                document_type__in=['EXPENSE', 'PURCHASE_ORDER']
            ),
            'purchases': Document.objects.filter(
                created_at__gte=twelve_months_ago,
                document_type='PURCHASE'
            ),
            'quotes': Document.objects.filter(
                created_at__gte=twelve_months_ago,
                document_type='QUOTE'
            )
        }

        # Initialize data arrays
        metrics_data = {metric: [0] * 12 for metric in metrics_docs.keys()}
        gross_profit_data = [0] * 12

        # Aggregate metrics by month
        for metric, docs in metrics_docs.items():
            metric_by_month = {}
            for doc in docs:
                month = doc.created_at.strftime('%b')
                if month not in metric_by_month:
                    metric_by_month[month] = 0
                metric_by_month[month] += float(doc.total_amount)

            # Map to data arrays
            for i, month in enumerate(month_labels):
                metrics_data[metric][i] = metric_by_month.get(month, 0)

        # Calculate Gross Profit
        for i in range(12):
            gross_profit_data[i] = (
                metrics_data['revenue'][i] - 
                metrics_data['purchases'][i]
            )

        # Prepare response
        response_data = {
            'labels': month_labels,
            'revenue': metrics_data['revenue'],
            'expenses': metrics_data['expenses'],
            'purchases': metrics_data['purchases'],
            'quotes': metrics_data['quotes'],
            'gross_profit': gross_profit_data
        }

        # Debug print
        print("\n--- Monthly Financial Trends Debug ---")
        for key, value in response_data.items():
            if key != 'labels':
                print(f"{key.upper()}: {value}")

        return JsonResponse(response_data)
