from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from ..models import Project, ProjectMilestone
from ..forms import ProjectMilestoneForm

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
            return redirect('project_management:project_detail', pk=project_pk)
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
            return redirect('project_management:project_detail', pk=milestone.project.pk)
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
        return redirect('project_management:project_detail', pk=project_pk)
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
        milestone.completion_percentage = 0
    milestone.save()
    
    # Update project completion percentage
    project = milestone.project
    total_milestones = project.milestones.count()
    if total_milestones > 0:
        completed_milestones = project.milestones.filter(is_completed=True).count()
        project.completion_percentage = (completed_milestones / total_milestones) * 100
        project.save()
    
    return JsonResponse({
        'status': 'success',
        'is_completed': milestone.is_completed,
        'completion_percentage': milestone.completion_percentage,
        'project_completion': project.completion_percentage
    })

@login_required
def milestone_update_percentage(request, pk):
    if request.method == 'POST':
        milestone = get_object_or_404(ProjectMilestone, pk=pk)
        try:
            percentage = int(request.POST.get('percentage', 0))
            if 0 <= percentage <= 100:
                milestone.completion_percentage = percentage
                if percentage == 100 and not milestone.is_completed:
                    milestone.is_completed = True
                    milestone.completed_date = timezone.now().date()
                elif percentage < 100 and milestone.is_completed:
                    milestone.is_completed = False
                    milestone.completed_date = None
                milestone.save()
                
                # Update project completion percentage
                project = milestone.project
                total_milestones = project.milestones.count()
                if total_milestones > 0:
                    total_percentage = sum(m.completion_percentage for m in project.milestones.all())
                    project.completion_percentage = total_percentage / total_milestones
                    project.save()
                
                return JsonResponse({
                    'status': 'success',
                    'completion_percentage': milestone.completion_percentage,
                    'is_completed': milestone.is_completed,
                    'project_completion': project.completion_percentage
                })
        except (ValueError, TypeError):
            pass
    return JsonResponse({'status': 'error'}, status=400) 