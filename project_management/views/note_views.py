from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..models import Project, ProjectNote
from ..forms import ProjectNoteForm

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
            return redirect('project_management:project_detail', pk=project_pk)
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
            return redirect('project_management:project_detail', pk=note.project.pk)
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
        return redirect('project_management:project_detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def note_toggle_pin(request, pk):
    note = get_object_or_404(ProjectNote, pk=pk)
    note.is_pinned = not note.is_pinned
    note.save()
    return JsonResponse({
        'status': 'success',
        'is_pinned': note.is_pinned
    }) 