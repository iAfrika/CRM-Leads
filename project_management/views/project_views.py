from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
from ..models import Project, ProjectDocument, ProjectNote, ProjectMilestone
from ..forms import ProjectForm, ProjectDocumentForm, ProjectNoteForm, ProjectMilestoneForm, ProjectFilterForm

@login_required
def project_list(request):
    projects = Project.objects.all()

    # Handle direct search and filter
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    
    # Apply filters
    if search:
        projects = projects.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(description__icontains=search) |
            Q(client__name__icontains=search) |
            Q(manager__username__icontains=search)
        )
    
    if status:
        projects = projects.filter(status=status)
    
    if priority:
        projects = projects.filter(priority=priority)
    
    # Check if no results found
    if not projects.exists() and (search or status or priority):
        no_results = True
    else:
        no_results = False

    context = {
        'projects': projects,
        'filter_form': {
            'search': search,
            'status': status,
            'priority': priority,
        },
        'no_results': no_results,
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
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Add success message and redirect with notification
            message = f"Project '{project.name}' created successfully."
            redirect_url = reverse('project_management:project_list') + f"?message={message}&type=success"
            return redirect(redirect_url)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
        'title': 'Create Project'
    }
    return render(request, 'project_management/project_form.html', context)

@login_required
@permission_required('project_management.change_project', raise_exception=True)
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            
            # Add success message and redirect with notification
            message = f"Project '{project.name}' updated successfully."
            redirect_url = reverse('project_management:project_list') + f"?message={message}&type=success"
            return redirect(redirect_url)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'title': f'Edit Project: {project.name}'
    }
    return render(request, 'project_management/project_form.html', context)

@login_required
@permission_required('project_management.delete_project', raise_exception=True)
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project_name = project.name
    
    if request.method == 'POST':
        project.delete()
        
        # Add success message and redirect with notification
        message = f"Project '{project_name}' deleted successfully."
        redirect_url = reverse('project_management:project_list') + f"?message={message}&type=success"
        return redirect(redirect_url)
    
    context = {
        'project': project,
        'title': f'Delete Project: {project.name}'
    }
    return render(request, 'project_management/project_confirm_delete.html', context)

@login_required
def project_finances(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Calculate financial metrics
    total_expenses = project.get_total_expenses()
    total_invoices = project.get_total_invoices()
    budget_utilization = project.get_budget_utilization()
    profit_margin = project.get_profit_margin()
    
    # Get project transactions
    transactions = project.transactions.all()
    
    context = {
        'project': project,
        'total_expenses': total_expenses,
        'total_invoices': total_invoices,
        'budget_utilization': budget_utilization,
        'profit_margin': profit_margin,
        'transactions': transactions,
        'title': f'Financial Overview: {project.name}'
    }
    return render(request, 'project_management/project_finances.html', context) 