from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Project, ProjectDocument, ProjectNote, ProjectMilestone, Transaction
from .forms import (
    ProjectForm, ProjectDocumentForm, ProjectNoteForm,
    ProjectMilestoneForm, ProjectFilterForm, TransactionForm
)
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

@login_required
def project_list(request):
    form = ProjectFilterForm(request.GET)
    projects = Project.objects.all()

    if form.is_valid():
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        client = form.cleaned_data.get('client')
        manager = form.cleaned_data.get('manager')
        date_range = form.cleaned_data.get('date_range')
        search = form.cleaned_data.get('search')

        if status:
            projects = projects.filter(status=status)
        if priority:
            projects = projects.filter(priority=priority)
        if client:
            projects = projects.filter(client=client)
        if manager:
            projects = projects.filter(manager=manager)
        if search:
            projects = projects.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                projects = projects.filter(start_date=today)
            elif date_range == 'week':
                week_start = today - timedelta(days=today.weekday())
                projects = projects.filter(start_date__gte=week_start)
            elif date_range == 'month':
                projects = projects.filter(start_date__year=today.year, start_date__month=today.month)
            elif date_range == 'quarter':
                quarter_start = datetime(today.year, ((today.month-1)//3)*3+1, 1).date()
                projects = projects.filter(start_date__gte=quarter_start)
            elif date_range == 'year':
                projects = projects.filter(start_date__year=today.year)

    context = {
        'projects': projects,
        'form': form,
        'title': 'Projects'
    }
    return render(request, 'project_management/project_list.html', context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    documents = project.documents.all()
    notes = project.project_notes.all()
    milestones = project.milestones.all()
    
    # Calculate project metrics
    total_expenses = project.get_total_expenses()
    total_invoices = project.get_total_invoices()
    budget_utilization = project.get_budget_utilization()
    profit_margin = project.get_profit_margin()
    
    context = {
        'project': project,
        'documents': documents,
        'notes': notes,
        'milestones': milestones,
        'total_expenses': total_expenses,
        'total_invoices': total_invoices,
        'budget_utilization': budget_utilization,
        'profit_margin': profit_margin,
        'title': f'Project: {project.name}'
    }
    return render(request, 'project_management/project_detail.html', context)

@login_required
@permission_required('project_management.add_project', raise_exception=True)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Project created successfully.')
            return redirect('project_management:detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'project_management/project_form.html', {
        'form': form,
        'title': 'Create Project'
    })

@login_required
@permission_required('project_management.change_project', raise_exception=True)
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_management:detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'project_management/project_form.html', {
        'form': form,
        'project': project,
        'title': f'Edit Project: {project.name}'
    })

@login_required
@permission_required('project_management.delete_project', raise_exception=True)
def project_delete(request, pk=None):
    """
    Delete a project with AJAX support and comprehensive error handling.
    
    Supports both GET and POST methods with optional primary key.
    Returns JSON response for AJAX requests.
    """
    if request.method == 'POST':
        # Determine project ID from URL parameter or POST data
        project_id = pk or request.POST.get('project_id')
        
        try:
            project = get_object_or_404(Project, pk=project_id)
            
            # Additional permission check
            if not request.user.has_perm('project_management.delete_project', project):
                return JsonResponse({
                    'status': 'error',
                    'message': 'You do not have permission to delete this project.'
                }, status=403)
            
            # Optional: Log project deletion
            logger.info(f"Project deleted: {project.name} by {request.user.username}")
            
            # Store project name before deletion for response
            project_name = project.name
            
            # Delete the project
            project.delete()
            
            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': f'Project "{project_name}" was successfully deleted.',
                'id': project_id
            })
        
        except ProtectedError:
            # Handle cases where project has related objects preventing deletion
            return JsonResponse({
                'status': 'error',
                'message': 'This project cannot be deleted due to existing related records.'
            }, status=400)
        
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Project deletion error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'An unexpected error occurred while deleting the project.'
            }, status=500)
    
    # Handle GET requests or invalid methods
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    }, status=405)

@login_required
def project_dashboard(request):
    # Get overall project statistics
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='in_progress').count()
    completed_projects = Project.objects.filter(status='completed').count()
    overdue_projects = Project.objects.filter(
        end_date__lt=timezone.now().date(),
        status__in=['planning', 'in_progress']
    ).count()

    # Get projects by status
    status_stats = Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Get projects by priority
    priority_stats = Project.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    # Get financial overview
    total_budget = Project.objects.aggregate(total=Sum('budget'))['total'] or 0
    total_actual_cost = Project.objects.aggregate(total=Sum('actual_cost'))['total'] or 0
    total_expenses = sum(project.get_total_expenses() for project in Project.objects.all())
    total_invoices = sum(project.get_total_invoices() for project in Project.objects.all())

    # Get recent projects (last 30 days)
    recent_projects = Project.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('-created_at')[:5]

    # Get real-time project data - active projects with recent updates
    realtime_projects = Project.objects.filter(
        status='in_progress',
        updated_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-updated_at')[:5]

    # Get projects with recent milestones completed
    recent_milestone_projects = Project.objects.filter(
        milestones__completed_date__gte=timezone.now() - timedelta(days=7),
        milestones__is_completed=True
    ).distinct().order_by('-milestones__completed_date')[:5]

    # Get projects with financial transactions in last 7 days
    recent_transaction_projects = Project.objects.filter(
        transactions__date__gte=timezone.now().date() - timedelta(days=7)
    ).annotate(
        recent_transaction_count=Count('transactions'),
        latest_transaction=models.Max('transactions__date')
    ).order_by('-latest_transaction')[:5]

    # Get upcoming milestones
    upcoming_milestones = ProjectMilestone.objects.filter(
        is_completed=False,
        due_date__gte=timezone.now().date()
    ).order_by('due_date')[:5]

    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'overdue_projects': overdue_projects,
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'total_budget': total_budget,
        'total_actual_cost': total_actual_cost,
        'total_expenses': total_expenses,
        'total_invoices': total_invoices,
        'recent_projects': recent_projects,
        'upcoming_milestones': upcoming_milestones,
        'realtime_projects': realtime_projects,
        'recent_milestone_projects': recent_milestone_projects,
        'recent_transaction_projects': recent_transaction_projects,
        'title': 'Project Dashboard'
    }
    return render(request, 'project_management/project_dashboard.html', context)

# Document management views
@login_required
def document_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('project_management:detail', pk=project_pk)
    else:
        form = ProjectDocumentForm()
    
    return render(request, 'project_management/document_form.html', {
        'form': form,
        'project': project,
        'title': 'Upload Document'
    })

@login_required
def document_delete(request, pk):
    document = get_object_or_404(ProjectDocument, pk=pk)
    project_pk = document.project.pk
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('project_management:detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

# Note management views
@login_required
def note_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.project = project
            note.created_by = request.user
            note.save()
            messages.success(request, 'Note added successfully.')
            return redirect('project_management:detail', pk=project_pk)
    else:
        form = ProjectNoteForm()
    
    return render(request, 'project_management/note_form.html', {
        'form': form,
        'project': project,
        'title': 'Add Note'
    })

@login_required
def note_update(request, pk):
    note = get_object_or_404(ProjectNote, pk=pk)
    if request.method == 'POST':
        form = ProjectNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note updated successfully.')
            return redirect('project_management:detail', pk=note.project.pk)
    else:
        form = ProjectNoteForm(instance=note)
    
    return render(request, 'project_management/note_form.html', {
        'form': form,
        'note': note,
        'project': note.project,
        'title': 'Edit Note'
    })

@login_required
def note_delete(request, pk):
    note = get_object_or_404(ProjectNote, pk=pk)
    project_pk = note.project.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted successfully.')
        return redirect('project_management:detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

# Milestone management views
@login_required
def milestone_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            messages.success(request, 'Milestone added successfully.')
            return redirect('project_management:detail', pk=project_pk)
    else:
        form = ProjectMilestoneForm()
    
    return render(request, 'project_management/milestone_form.html', {
        'form': form,
        'project': project,
        'title': 'Add Milestone'
    })

@login_required
def milestone_update(request, pk):
    milestone = get_object_or_404(ProjectMilestone, pk=pk)
    if request.method == 'POST':
        form = ProjectMilestoneForm(request.POST, instance=milestone)
        if form.is_valid():
            form.save()
            messages.success(request, 'Milestone updated successfully.')
            return redirect('project_management:detail', pk=milestone.project.pk)
    else:
        form = ProjectMilestoneForm(instance=milestone)
    
    return render(request, 'project_management/milestone_form.html', {
        'form': form,
        'milestone': milestone,
        'project': milestone.project,
        'title': 'Edit Milestone'
    })

@login_required
def milestone_delete(request, pk):
    milestone = get_object_or_404(ProjectMilestone, pk=pk)
    project_pk = milestone.project.pk
    if request.method == 'POST':
        milestone.delete()
        messages.success(request, 'Milestone deleted successfully.')
        return redirect('project_management:detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def milestone_toggle(request, pk):
    milestone = get_object_or_404(ProjectMilestone, pk=pk)
    milestone.is_completed = not milestone.is_completed
    if milestone.is_completed:
        milestone.completed_date = timezone.now().date()
        milestone.completion_percentage = 100
    else:
        milestone.completed_date = None
    milestone.save()
    return JsonResponse({
        'status': 'success',
        'is_completed': milestone.is_completed,
        'completion_percentage': milestone.completion_percentage
    })

# Financial management views
@login_required
def project_finances(request, pk):
    """View project finances with transactions"""
    project = get_object_or_404(Project, pk=pk)
    transactions = Transaction.objects.filter(project=project).order_by('-date')
    
    context = {
        'project': project,
        'transactions': transactions,
        'title': f'Project Finances: {project.name}'
    }
    return render(request, 'project_management/project_finances.html', context)

def finance_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    context = {
        'transaction': transaction,
    }
    return render(request, 'project_management/transaction_detail.html', context)

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

def finance_create(request, project_pk):
    """Create a new transaction for a project"""
    project = get_object_or_404(Project, pk=project_pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.project = project
            transaction.save()
            
            messages.success(request, "Transaction added successfully.")
            
            # For AJAX requests, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
                
            return redirect('project_management:project_finances', pk=project.pk)
    else:
        form = TransactionForm()
    
    context = {
        'form': form,
        'project': project,
        'title': 'Add Transaction'
    }
    return render(request, 'project_management/finance_form.html', context)

def finance_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully.")
            
            # For AJAX requests, return simple success response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
                
            return redirect('project_management:project_finances', pk=transaction.project.pk)
    else:
        form = TransactionForm(instance=transaction)
    
    context = {
        'form': form,
        'transaction': transaction,
    }
    return render(request, 'project_management/finance_form.html', context)

@login_required
def finance_delete(request, pk):
    """Delete a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk)
    project_pk = transaction.project.pk
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction deleted successfully.")
        return redirect('project_management:project_finances', pk=project_pk)
    
    # If not POST, return JSON error
    return JsonResponse({'status': 'error'}, status=405)
