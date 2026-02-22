from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import Purchase, PurchaseCategory
from .forms import PurchaseForm, PurchaseCategoryForm
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import redirect
from decimal import Decimal
from documents.models import Document  # Corrected import
import logging

logger = logging.getLogger(__name__)

@login_required
def purchase_list(request):
    if request.user.is_superuser:
        purchases = Purchase.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        purchases = Purchase.objects.filter(profile_id=request.profile.id)
    else:
        purchases = Purchase.objects.filter(created_by_id=request.user.id)
    
    total_amount = purchases.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Filter categories by profile if not superuser
    if request.user.is_superuser:
        categories = PurchaseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = PurchaseCategory.objects.filter(profile_id=request.profile.id)
    else:
        categories = PurchaseCategory.objects.filter(created_by_id=request.user.id)
    
    context = {
        'purchases': purchases,
        'total_amount': total_amount,
        'categories': categories,
    }
    return render(request, 'purchases/purchase_list.html', context)

@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # Check if user has permission to view this purchase
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if purchase.profile != request.profile:
                messages.error(request, "You don't have permission to view this purchase.")
                return redirect('purchases:purchase_list')
        elif purchase.created_by != request.user:
            messages.error(request, "You don't have permission to view this purchase.")
            return redirect('purchases:purchase_list')
    
    return render(request, 'purchases/purchase_detail.html', {'purchase': purchase})

@login_required
def purchase_create(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST, request.FILES)
        if form.is_valid():
            purchase = form.save(commit=False)
            purchase.created_by = request.user
            if hasattr(request, 'profile') and request.profile:
                purchase.profile = request.profile
            purchase.save()
            messages.success(request, 'Purchase created successfully!')
            return redirect('purchases:purchase_list')
    else:
        form = PurchaseForm()
        
        # Filter categories by profile if not superuser
        if not request.user.is_superuser:
            if hasattr(request, 'profile') and request.profile:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(profile_id=request.profile.id)
            else:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(created_by_id=request.user.id)
    
    return render(request, 'purchases/purchase_form.html', {
        'form': form,
        'title': 'Create Purchase'
    })

@login_required
def purchase_update(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # Check if user has permission to update this purchase
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if purchase.profile != request.profile:
                messages.error(request, "You don't have permission to update this purchase.")
                return redirect('purchases:purchase_list')
        elif purchase.created_by != request.user:
            messages.error(request, "You don't have permission to update this purchase.")
            return redirect('purchases:purchase_list')
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, request.FILES, instance=purchase)
        if form.is_valid():
            purchase = form.save(commit=False)
            # Don't change the created_by field, but update profile if needed
            if hasattr(request, 'profile') and request.profile:
                purchase.profile = request.profile
            purchase.save()
            messages.success(request, 'Purchase updated successfully!')
            return redirect('purchases:purchase_detail', pk=purchase.pk)
    else:
        form = PurchaseForm(instance=purchase)
        
        # Filter categories by profile if not superuser
        if not request.user.is_superuser:
            if hasattr(request, 'profile') and request.profile:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(profile_id=request.profile.id)
            else:
                form.fields['category'].queryset = PurchaseCategory.objects.filter(created_by_id=request.user.id)
    
    return render(request, 'purchases/purchase_form.html', {
        'form': form,
        'purchase': purchase,
        'title': 'Update Purchase'
    })

@login_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # Check if user has permission to delete this purchase
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if purchase.profile != request.profile:
                messages.error(request, "You don't have permission to delete this purchase.")
                return redirect('purchases:purchase_list')
        elif purchase.created_by != request.user:
            messages.error(request, "You don't have permission to delete this purchase.")
            return redirect('purchases:purchase_list')
    
    if request.method == 'POST':
        purchase.delete()
        messages.success(request, 'Purchase deleted successfully!')
        return redirect('purchases:purchase_list')
    return render(request, 'purchases/purchase_confirm_delete.html', {'purchase': purchase})

@login_required
def category_list(request):
    if request.method == 'POST':
        form = PurchaseCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            if hasattr(request, 'profile') and request.profile:
                category.profile = request.profile
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('purchases:category_list')
    else:
        form = PurchaseCategoryForm()
    
    # Get categories
    if request.user.is_superuser:
        categories = PurchaseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = PurchaseCategory.objects.filter(profile_id=request.profile.id)
    else:
        categories = PurchaseCategory.objects.filter(created_by_id=request.user.id)
    
    return render(request, 'purchases/category_list.html', {
        'categories': categories,
        'form': form
    })

@login_required
def category_create(request):
    if request.method == 'POST':
        form = PurchaseCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            if hasattr(request, 'profile') and request.profile:
                category.profile = request.profile
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('purchases:category_list')
    else:
        form = PurchaseCategoryForm()
    
    return render(request, 'purchases/category_form.html', {
        'form': form,
        'title': 'Create Category'
    })

@login_required
def category_update(request, pk):
    category = get_object_or_404(PurchaseCategory, pk=pk)
    
    # Check if user has permission to update this category
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if category.profile != request.profile:
                messages.error(request, "You don't have permission to update this category.")
                return redirect('purchases:category_list')
        elif category.created_by != request.user:
            messages.error(request, "You don't have permission to update this category.")
            return redirect('purchases:category_list')
    
    if request.method == 'POST':
        form = PurchaseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('purchases:category_list')
    else:
        form = PurchaseCategoryForm(instance=category)
    
    return render(request, 'purchases/category_form.html', {
        'form': form,
        'category': category,
        'title': 'Update Category'
    })

@login_required
def category_delete(request, pk):
    category = get_object_or_404(PurchaseCategory, pk=pk)
    
    # Check if user has permission to delete this category
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if category.profile != request.profile:
                messages.error(request, "You don't have permission to delete this category.")
                return redirect('purchases:category_list')
        elif category.created_by != request.user:
            messages.error(request, "You don't have permission to delete this category.")
            return redirect('purchases:category_list')
    
    # Check if there are any purchases associated with this category
    if Purchase.objects.filter(category=category).exists():
        messages.error(request, "Cannot delete this category because it has associated purchases.")
        return redirect('purchases:category_list')
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('purchases:category_list')
    
    return render(request, 'purchases/category_confirm_delete.html', {'category': category})

@login_required
def purchase_reports(request):
    # Get the selected period
    period = request.GET.get('period', 'month')
    
    # Define date range based on period
    today = timezone.now().date()
    if period == 'month':
        start_date = today.replace(day=1)
        period_label = 'This Month'
    elif period == 'quarter':
        current_quarter = (today.month - 1) // 3 + 1
        start_date = today.replace(month=(current_quarter - 1) * 3 + 1, day=1)
        period_label = f'Q{current_quarter} {today.year}'
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        period_label = f'Year {today.year}'
    else:  # 'all'
        start_date = None
        period_label = 'All Time'
    
    # Get purchases based on user and period
    if request.user.is_superuser:
        purchases_query = Purchase.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        purchases_query = Purchase.objects.filter(profile_id=request.profile.id)
    else:
        purchases_query = Purchase.objects.filter(created_by_id=request.user.id)
    
    # Apply date filter if needed
    if start_date:
        purchases_query = purchases_query.filter(date__range=[start_date, today])
    
    # Monthly purchases
    monthly_purchases = purchases_query.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Category wise purchases
    category_purchases = purchases_query.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Status wise purchases
    status_purchases = purchases_query.values('status').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Vendor wise purchases
    vendor_purchases = purchases_query.values('vendor').annotate(
        total=Sum('amount'),
        count=Sum('quantity')
    ).order_by('-total')[:10]  # Top 10 vendors
    
    return render(request, 'purchases/purchase_reports.html', {
        'monthly_purchases': monthly_purchases,
        'category_purchases': category_purchases,
        'status_purchases': status_purchases,
        'vendor_purchases': vendor_purchases,
        'total_amount': purchases_query.aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_count': purchases_query.count(),
        'start_date': start_date,
        'end_date': today,
        'date_range': period,
        'period_label': period_label,
    })

@login_required
def generate_purchase_order(request, pk):
    """Generate a Purchase Order document from a Purchase"""
    try:
        # Detailed logging of request and input
        logger.info(f"Generating Purchase Order - Request User: {request.user}")
        logger.info(f"Generating Purchase Order - Purchase ID: {pk}")
        
        # Get the purchase with more detailed logging
        try:
            purchase = Purchase.objects.select_related('category').get(pk=pk)
            logger.info(f"Purchase found: {purchase}")
            logger.info(f"Purchase Details:")
            logger.info(f"  Title: {purchase.title}")
            logger.info(f"  Amount: {purchase.amount}")
            logger.info(f"  Date: {purchase.date}")
            logger.info(f"  Category: {purchase.category}")
            
            # Additional logging for profile and created_by
            if hasattr(purchase, 'profile'):
                logger.info(f"  Profile: {purchase.profile}")
            if hasattr(purchase, 'created_by'):
                logger.info(f"  Created By: {purchase.created_by}")
        except Purchase.DoesNotExist:
            logger.error(f"Purchase with ID {pk} does not exist")
            messages.error(request, "Purchase not found.")
            return redirect('purchases:purchase_list')
        except Exception as e:
            logger.error(f"Error retrieving purchase: {str(e)}")
            messages.error(request, f"Error retrieving purchase: {str(e)}")
            return redirect('purchases:purchase_list')
        
        # Check permissions with more detailed logging
        if not request.user.is_superuser:
            # Check profile-based permissions
            try:
                if hasattr(request, 'profile') and request.profile:
                    # Check if purchase has a profile and if it matches
                    if hasattr(purchase, 'profile') and purchase.profile:
                        if purchase.profile != request.profile:
                            logger.warning(f"Permission denied: Profile mismatch. User Profile: {request.profile}, Purchase Profile: {purchase.profile}")
                            messages.error(request, "You don't have permission to generate a purchase order.")
                            return redirect('purchases:purchase_detail', pk=pk)
                
                # Check user-based permissions
                if hasattr(purchase, 'created_by') and purchase.created_by:
                    if purchase.created_by != request.user:
                        logger.warning(f"Permission denied: User mismatch. Request User: {request.user}, Purchase Created By: {purchase.created_by}")
                        messages.error(request, "You don't have permission to generate a purchase order.")
                        return redirect('purchases:purchase_detail', pk=pk)
            except Exception as perm_error:
                logger.error(f"Error checking purchase permissions: {str(perm_error)}")
                messages.error(request, "An error occurred while checking permissions.")
                return redirect('purchases:purchase_detail', pk=pk)
        
        # Check if document already exists
        logger.info(f"Checking for existing Purchase Order for Purchase {pk}")
        existing_doc_query = Document.objects.filter(purchase=purchase, document_type='PURCHASE_ORDER')
        logger.info(f"Existing Document Query: {existing_doc_query.query}")
        existing_doc = existing_doc_query.first()
        logger.info(f"Existing Document Query Result: {existing_doc}")
        if existing_doc:
            logger.info(f"Purchase Order already exists for Purchase {pk}. Existing Document ID: {existing_doc.pk}")
            messages.info(request, "A Purchase Order document already exists for this purchase.")
            return redirect('documents:purchase_order_detail', pk=existing_doc.pk)
        
        # Create the document with detailed logging
        try:
            document = Document.objects.create(
                client=None,  # Client is not required
                document_type='PURCHASE_ORDER',
                description=f"Purchase Order for {purchase.title}",
                subtotal=purchase.amount,
                tax_rate=Decimal('0.00'),
                tax_amount=Decimal('0.00'),
                total_amount=purchase.amount,
                document_date=purchase.date or timezone.now().date(),
                status='DRAFT',
                purchase=purchase,
                created_by_id=request.user.id
            )
            logger.info(f"Successfully created Purchase Order Document. ID: {document.pk}")
            messages.success(request, "Purchase Order document generated successfully.")
            return redirect('documents:purchase_order_detail', pk=document.pk)
        except Exception as doc_error:
            logger.error(f"Failed to create Purchase Order Document: {str(doc_error)}")
            messages.error(request, f"Failed to generate Purchase Order. Error: {str(doc_error)}")
            return redirect('purchases:purchase_detail', pk=pk)
    
    except Exception as e:
        # Comprehensive error logging
        logger.error(f"Comprehensive error in generate_purchase_order for Purchase {pk}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Provide a user-friendly error message
        messages.error(request, f"Unexpected error generating Purchase Order. Please contact support.")
        return redirect('purchases:purchase_detail', pk=pk)
