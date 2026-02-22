from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from ..models import Project, Transaction
from ..forms import TransactionForm

@login_required
def finance_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.project = project
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            
            # For AJAX requests, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
                
            return redirect('project_management:project_finances', pk=project_pk)
    else:
        form = TransactionForm()
    
    return render(request, 'project_management/finance_form.html', {
        'form': form,
        'project': project,
        'title': 'Add Transaction'
    })

@login_required
def finance_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            
            # For AJAX requests, return simple success response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
                
            return redirect('project_management:project_finances', pk=transaction.project.pk)
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'project_management/finance_form.html', {
        'form': form,
        'project': transaction.project,
        'title': 'Update Transaction'
    })

@login_required
def finance_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    project_pk = transaction.project.pk
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('project_management:project_finances', pk=project_pk)
    
    # If not POST, return JSON error
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def finance_get(request, pk):
    """API endpoint to get transaction data for the edit form"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return HttpResponseBadRequest('Invalid request')
        
    transaction = get_object_or_404(Transaction, pk=pk)
    data = {
        'date': transaction.date.strftime('%Y-%m-%d'),
        'description': transaction.description,
        'transaction_type': transaction.transaction_type,
        'amount': float(transaction.amount),
    }
    
    return JsonResponse(data) 