from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import Expense, ExpenseCategory, RecurringExpense
from .forms import ExpenseForm, ExpenseCategoryForm, RecurringExpenseForm
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import redirect
from decimal import Decimal
from documents.models import Document  # Corrected import
import logging

logger = logging.getLogger(__name__)

@login_required
def expense_list(request):
    if request.user.is_superuser:
        expenses = Expense.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        expenses = Expense.objects.filter(profile_id=request.profile.id)
    else:
        expenses = Expense.objects.filter(created_by_id=request.user.id)
    
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Filter categories by profile if not superuser
    if request.user.is_superuser:
        categories = ExpenseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = ExpenseCategory.objects.filter(profile_id=request.profile.id)
    else:
        categories = ExpenseCategory.objects.filter(created_by_id=request.user.id)
    
    context = {
        'expenses': expenses,
        'total_amount': total_amount,
        'categories': categories,
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    # Check if user has permission to view this expense
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if expense.profile != request.profile:
                messages.error(request, "You don't have permission to view this expense.")
                return redirect('expenses:expense_list')
        elif expense.created_by != request.user:
            messages.error(request, "You don't have permission to view this expense.")
            return redirect('expenses:expense_list')
    
    return render(request, 'expenses/expense_detail.html', {'expense': expense})

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by_id = request.user.id
            if hasattr(request, 'profile') and request.profile:
                expense.profile_id = request.profile.id
            expense.save()
            messages.success(request, 'Expense created successfully!')
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm()
        
        # Filter categories by profile if not superuser
        if not request.user.is_superuser:
            if hasattr(request, 'profile') and request.profile:
                form.fields['category'].queryset = ExpenseCategory.objects.filter(profile_id=request.profile.id)
            else:
                form.fields['category'].queryset = ExpenseCategory.objects.filter(created_by_id=request.user.id)
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'title': 'Create Expense'
    })

@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    # Check if user has permission to update this expense
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if expense.profile_id != request.profile.id:
                messages.error(request, "You don't have permission to update this expense.")
                return redirect('expenses:expense_list')
        elif expense.created_by_id != request.user.id:
            messages.error(request, "You don't have permission to update this expense.")
            return redirect('expenses:expense_list')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            expense = form.save(commit=False)
            # Don't change the created_by field, but update profile if needed
            if hasattr(request, 'profile') and request.profile:
                expense.profile_id = request.profile.id
            expense.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
        
        # Filter categories by profile if not superuser
        if not request.user.is_superuser:
            if hasattr(request, 'profile') and request.profile:
                form.fields['category'].queryset = ExpenseCategory.objects.filter(profile_id=request.profile.id)
            else:
                form.fields['category'].queryset = ExpenseCategory.objects.filter(created_by_id=request.user.id)
    
    return render(request, 'expenses/expense_form.html', {
        'form': form,
        'expense': expense,
        'title': 'Update Expense'
    })

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    
    # Check if user has permission to delete this expense
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if expense.profile != request.profile:
                messages.error(request, "You don't have permission to delete this expense.")
                return redirect('expenses:expense_list')
        elif expense.created_by != request.user:
            messages.error(request, "You don't have permission to delete this expense.")
            return redirect('expenses:expense_list')
    
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return redirect('expenses:expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

@login_required
def category_list(request):
    if request.method == 'POST':
        # Check if we're editing an existing category
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if category_id:
            # Editing an existing category
            category = get_object_or_404(ExpenseCategory, pk=category_id)
            
            # Check if user has permission to edit this category
            if not request.user.is_superuser:
                if hasattr(request, 'profile') and request.profile:
                    if category.profile != request.profile:
                        messages.error(request, "You don't have permission to edit this category.")
                        return redirect('expenses:category_list')
                elif category.created_by != request.user:
                    messages.error(request, "You don't have permission to edit this category.")
                    return redirect('expenses:category_list')
            
            category.name = name
            category.description = description
            category.save()
            messages.success(request, 'Category updated successfully!')
        elif name:
            # Creating a new category
            category = ExpenseCategory(
                name=name,
                description=description,
                created_by_id=request.user.id
            )
            if hasattr(request, 'profile') and request.profile:
                category.profile_id = request.profile.id
            category.save()
            messages.success(request, 'Category created successfully!')
        
        return redirect('expenses:category_list')
    
    # Get categories
    if request.user.is_superuser:
        categories = ExpenseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = ExpenseCategory.objects.filter(profile_id=request.profile.id)
    else:
        categories = ExpenseCategory.objects.filter(created_by_id=request.user.id)
    
    # Calculate total amount for each category
    for category in categories:
        category.total_amount = Expense.objects.filter(category=category).aggregate(Sum('amount'))['amount__sum'] or 0
    
    return render(request, 'expenses/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ExpenseCategory.objects.create(name=name)
            messages.success(request, 'Category added successfully.')
        return redirect('expenses:category_list')

@login_required
def category_edit(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            messages.success(request, 'Category updated successfully.')
        return redirect('expenses:category_list')

@login_required
def category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    # Check if there are any expenses associated with this category
    if Expense.objects.filter(category=category).exists():
        messages.error(request, "Cannot delete this category because it has associated expenses.")
        return redirect('expenses:category_list')

    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('expenses:category_list')

@login_required
def recurring_expense_list(request):
    # Filter recurring expenses by profile if not superuser
    if request.user.is_superuser:
        recurring_expenses = RecurringExpense.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        recurring_expenses = RecurringExpense.objects.filter(profile_id=request.profile.id)
    else:
        recurring_expenses = RecurringExpense.objects.filter(created_by_id=request.user.id)
    
    # Get categories for the dropdown
    if request.user.is_superuser:
        categories = ExpenseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = ExpenseCategory.objects.filter(profile_id=request.profile.id)
    else:
        categories = ExpenseCategory.objects.filter(created_by_id=request.user.id)
    
    return render(request, 'expenses/recurring_expense_list.html', {
        'recurring_expenses': recurring_expenses,
        'categories': categories,
    })

@login_required
def recurring_expense_create(request):
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        frequency = request.POST.get('frequency')
        next_date = request.POST.get('next_date')
        
        try:
            # Get the category
            category = ExpenseCategory.objects.get(id=category_id)
            
            # Create a new recurring expense
            recurring_expense = RecurringExpense(
                title=title,
                amount=float(amount),
                category=category,
                frequency=frequency,
                next_date=next_date,
                created_by_id=request.user.id
            )
            
            # Set profile if available
            if hasattr(request, 'profile') and request.profile:
                recurring_expense.profile_id = request.profile.id
                
            recurring_expense.save()
            messages.success(request, 'Recurring expense created successfully.')
            return redirect('expenses:recurring_expense_list')
        except Exception as e:
            messages.error(request, f'Error creating recurring expense: {str(e)}')
    
    return redirect('expenses:recurring_expense_list')

@login_required
def recurring_expense_update(request, pk):
    recurring_expense = get_object_or_404(RecurringExpense, pk=pk)
    
    # Check if user has permission to update this recurring expense
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if recurring_expense.profile != request.profile:
                messages.error(request, "You don't have permission to update this recurring expense.")
                return redirect('expenses:recurring_expense_list')
        elif recurring_expense.created_by != request.user:
            messages.error(request, "You don't have permission to update this recurring expense.")
            return redirect('expenses:recurring_expense_list')
    
    # Get categories for the dropdown
    if request.user.is_superuser:
        categories = ExpenseCategory.objects.all()
    elif hasattr(request, 'profile') and request.profile:
        categories = ExpenseCategory.objects.filter(profile_id=request.profile.id)
    else:
        categories = ExpenseCategory.objects.filter(created_by_id=request.user.id)
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            amount = request.POST.get('amount')
            category_id = request.POST.get('category')
            frequency = request.POST.get('frequency')
            next_date = request.POST.get('next_date')
            is_active = request.POST.get('is_active', 'True') == 'True'
            
            # Get the category
            category = ExpenseCategory.objects.get(id=category_id)
            
            # Update the recurring expense
            recurring_expense.title = title
            recurring_expense.amount = float(amount)
            recurring_expense.category = category
            recurring_expense.frequency = frequency
            recurring_expense.next_date = next_date
            recurring_expense.is_active = is_active
            
            # Don't change the created_by field, but update profile if needed
            if hasattr(request, 'profile') and request.profile:
                recurring_expense.profile = request.profile
                
            recurring_expense.save()
            messages.success(request, 'Recurring expense updated successfully!')
            return redirect('expenses:recurring_expense_list')
        except Exception as e:
            messages.error(request, f'Error updating recurring expense: {str(e)}')
    
    return render(request, 'expenses/recurring_expense_form.html', {
        'recurring_expense': recurring_expense,
        'categories': categories,
    })

@login_required
def recurring_expense_delete(request, pk):
    recurring_expense = get_object_or_404(RecurringExpense, pk=pk)
    
    # Check if user has permission to delete this recurring expense
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if recurring_expense.profile != request.profile:
                messages.error(request, "You don't have permission to delete this recurring expense.")
                return redirect('expenses:recurring_expense_list')
        elif recurring_expense.created_by != request.user:
            messages.error(request, "You don't have permission to delete this recurring expense.")
            return redirect('expenses:recurring_expense_list')
    
    if request.method == 'POST':
        recurring_expense.delete()
        messages.success(request, 'Recurring expense deleted successfully!')
        return redirect('expenses:recurring_expense_list')
    
    return render(request, 'expenses/recurring_expense_confirm_delete.html', {'recurring_expense': recurring_expense})

@login_required
def recurring_expense_toggle(request, pk):
    recurring_expense = get_object_or_404(RecurringExpense, pk=pk)
    
    # Check if user has permission to toggle this recurring expense
    if not request.user.is_superuser:
        if hasattr(request, 'profile') and request.profile:
            if recurring_expense.profile != request.profile:
                messages.error(request, "You don't have permission to toggle this recurring expense.")
                return redirect('expenses:recurring_expense_list')
        elif recurring_expense.created_by != request.user:
            messages.error(request, "You don't have permission to toggle this recurring expense.")
            return redirect('expenses:recurring_expense_list')
    
    # Toggle the active status
    recurring_expense.is_active = not recurring_expense.is_active
    recurring_expense.save()
    
    status = "activated" if recurring_expense.is_active else "paused"
    messages.success(request, f'Recurring expense {status} successfully!')
    
    return redirect('expenses:recurring_expense_list')

@login_required
def expense_reports(request):
    # Get the date range from request or default to last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Monthly expenses
    monthly_expenses = Expense.objects.filter(
        created_by_id=request.user.id,
        date__range=[start_date, end_date]
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Category wise expenses
    category_expenses = Expense.objects.filter(
        created_by_id=request.user.id,
        date__range=[start_date, end_date]
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    return render(request, 'expenses/expense_reports.html', {
        'monthly_expenses': monthly_expenses,
        'category_expenses': category_expenses,
        'start_date': start_date,
        'end_date': end_date
    })

@login_required
def generate_expense_sheet(request, pk):
    """Generate an Expense Sheet document from an Expense"""
    try:
        expense = get_object_or_404(Expense, pk=pk)
        
        # Log detailed expense information
        logger.info(f"Attempting to generate expense sheet for Expense {pk}")
        logger.info(f"Expense details: Title: {expense.title}, Amount: {expense.amount}, Date: {expense.date}")
        logger.info(f"Expense Category: {expense.category}")
        logger.info(f"Expense Profile: {expense.profile}")
        logger.info(f"Expense Created By: {expense.created_by}")
        
        # Check permissions
        if not request.user.is_superuser:
            if hasattr(request, 'profile') and request.profile:
                if expense.profile and expense.profile != request.profile:
                    logger.warning(f"Permission denied: Profile mismatch for Expense {pk}")
                    messages.error(request, "You don't have permission to generate an expense sheet.")
                    return redirect('expenses:expense_detail', pk=pk)
            elif expense.created_by != request.user:
                logger.warning(f"Permission denied: User mismatch for Expense {pk}")
                messages.error(request, "You don't have permission to generate an expense sheet.")
                return redirect('expenses:expense_detail', pk=pk)
        
        # Check if document already exists
        existing_doc = Document.objects.filter(expense=expense, document_type='EXPENSE_SHEET').first()
        if existing_doc:
            logger.info(f"Expense Sheet already exists for Expense {pk}")
            messages.info(request, "An Expense Sheet document already exists for this expense.")
            return redirect('documents:expense_sheet_detail', pk=existing_doc.pk)
        
        # Create the document
        try:
            document = Document.objects.create(
                client=None,  # Client is not required
                document_type='EXPENSE_SHEET',
                description=f"Expense Sheet for {expense.title}",
                subtotal=expense.amount,
                tax_rate=Decimal('0.00'),
                tax_amount=Decimal('0.00'),
                total_amount=expense.amount,
                document_date=expense.date or timezone.now().date(),
                status='DRAFT',
                expense=expense,
                created_by_id=request.user.id
            )
            logger.info(f"Successfully generated Expense Sheet for Expense {pk}. Document ID: {document.pk}")
            messages.success(request, "Expense Sheet document generated successfully.")
            return redirect('documents:expense_sheet_detail', pk=document.pk)
        except Exception as e:
            logger.error(f"Failed to generate Expense Sheet for Expense {pk}: {str(e)}")
            messages.error(request, f"Failed to generate Expense Sheet: {str(e)}")
            return redirect('expenses:expense_detail', pk=pk)
    
    except Exception as e:
        # Log the full error details
        logger.error(f"Comprehensive error in generate_expense_sheet for Expense {pk}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Provide a user-friendly error message
        messages.error(request, f"Failed to generate Expense Sheet. Please contact support. Error: {str(e)}")
        return redirect('expenses:expense_detail', pk=pk)
