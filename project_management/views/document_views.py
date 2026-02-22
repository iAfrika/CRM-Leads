from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from ..models import Project, ProjectDocument
from ..forms import ProjectDocumentForm

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
            return redirect('project_management:project_detail', pk=project_pk)
    else:
        form = ProjectDocumentForm()
    
    return render(request, 'project_management/document_form.html', {
        'form': form,
        'project': project,
        'title': 'Upload Document'
    })

@login_required
def document_update(request, pk):
    document = get_object_or_404(ProjectDocument, pk=pk)
    if request.method == 'POST':
        form = ProjectDocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document updated successfully.')
            return redirect('project_management:project_detail', pk=document.project.pk)
    else:
        form = ProjectDocumentForm(instance=document)
    
    return render(request, 'project_management/document_form.html', {
        'form': form,
        'document': document,
        'project': document.project,
        'title': 'Edit Document'
    })

@login_required
def document_delete(request, project_pk, pk):
    document = get_object_or_404(ProjectDocument, pk=pk, project_id=project_pk)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully.')
        return redirect('project_management:project_detail', pk=project_pk)
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def document_download(request, pk):
    document = get_object_or_404(ProjectDocument, pk=pk)
    response = HttpResponse(document.file, content_type='application/force-download')
    response['Content-Disposition'] = f'attachment; filename="{document.file.name}"'
    return response 