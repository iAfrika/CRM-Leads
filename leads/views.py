from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from .models import Lead, LeadActivity, LeadNote, LeadDocument, Client
from .forms import (
    LeadForm, 
    LeadActivityForm, 
    LeadFilterForm, 
    LeadNoteForm, 
    LeadDocumentForm
)
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView, 
    TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import View

# Create your views here.

@login_required
def lead_list(request):
    form = LeadFilterForm(request.GET)
    leads = Lead.objects.all()

    if form.is_valid():
        status = form.cleaned_data.get('status')
        source = form.cleaned_data.get('source')
        priority = form.cleaned_data.get('priority')
        assigned_to = form.cleaned_data.get('assigned_to')
        date_range = form.cleaned_data.get('date_range')
        search = form.cleaned_data.get('search')

        if status:
            leads = leads.filter(status=status)
        if source:
            leads = leads.filter(source=source)
        if priority:
            leads = leads.filter(priority=priority)
        if assigned_to:
            leads = leads.filter(assigned_to=assigned_to)
        if search:
            leads = leads.filter(
                Q(company_name__icontains=search) |
                Q(contact_person__icontains=search) |
                Q(email__icontains=search) |
                Q(description__icontains=search)
            )
        
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                leads = leads.filter(created_at__date=today)
            elif date_range == 'week':
                week_start = today - timedelta(days=today.weekday())
                leads = leads.filter(created_at__date__gte=week_start)
            elif date_range == 'month':
                leads = leads.filter(created_at__year=today.year, created_at__month=today.month)
            elif date_range == 'quarter':
                quarter_start = datetime(today.year, ((today.month-1)//3)*3+1, 1).date()
                leads = leads.filter(created_at__date__gte=quarter_start)
            elif date_range == 'year':
                leads = leads.filter(created_at__year=today.year)

    context = {
        'leads': leads,
        'form': form,
        'title': 'Leads'
    }
    return render(request, 'leads/lead_list.html', context)

@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    activities = lead.activities.all()
    activity_form = LeadActivityForm()
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'add_note':
            note_form = LeadNoteForm(request.POST)
            if note_form.is_valid():
                note = note_form.save(commit=False)
                note.lead = lead
                note.created_by_id = request.user.id
                note.save()
                messages.success(request, 'Note added successfully.')
                return redirect('leads:lead_detail', pk=pk)
            else:
                print("Note Form Errors:", note_form.errors)
                messages.error(request, 'Error adding note. Please check the form.')
                
        elif action == 'add_document':
            document_form = LeadDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                document = document_form.save(commit=False)
                document.lead = lead
                document.created_by_id = request.user.id
                document.save()
                messages.success(request, 'Document uploaded successfully.')
                return redirect('leads:lead_detail', pk=pk)
            else:
                print("Document Form Errors:", document_form.errors)
                messages.error(request, 'Error uploading document. Please check the form.')
        else:
            activity_form = LeadActivityForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                activity.lead = lead
                activity.created_by_id = request.user.id
                activity.save()
                messages.success(request, 'Activity added successfully.')
                return redirect('leads:lead_detail', pk=pk)
    
    context = {
        'lead': lead,
        'title': f'Lead: {lead.title or lead.company_name}',
        'activities': activities,
        'activity_form': activity_form,
        'documents': lead.documents.all(),
        'notes': lead.notes.all()
    }
    return render(request, 'leads/lead_detail.html', context)

@login_required
@permission_required('leads.add_lead', raise_exception=True)
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.created_by_id = request.user.id
            lead.save()
            messages.success(request, f'Lead "{lead.title or lead.company_name}" created successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'title': 'Create Lead'
    }
    return render(request, 'leads/lead_form.html', context)

@login_required
@permission_required('leads.change_lead', raise_exception=True)
def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm(instance=lead)
    
    return render(request, 'leads/lead_form.html', {
        'form': form,
        'lead': lead,
        'title': f'Edit Lead: {lead.title or lead.company_name}'
    })

@login_required
@permission_required('leads.delete_lead', raise_exception=True)
def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully.')
        return redirect('leads:lead_list')
    return render(request, 'leads/lead_confirm_delete.html', {
        'lead': lead,
        'title': f'Delete Lead: {lead.title or lead.company_name}'
    })

@login_required
def lead_convert(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if lead.status != 'won':
        messages.error(request, 'Only won leads can be converted to clients.')
        return redirect('leads:lead_detail', pk=pk)
    
    try:
        # Create new client from lead data
        client = Client.objects.create(
            name=lead.company_name,  # Company name goes to name field
            contact_person=lead.contact_person,  # Contact person field exists
            email=lead.email,
            phone=lead.phone
        )
        
        # Update lead status
        lead.status = 'CONVERTED'
        lead.save()
        
        # Create activity record
        LeadActivity.objects.create(
            lead=lead,
            activity_type='converted',
            description=f'Lead converted to client: {client.name}',
            created_by_id=request.user.id
        )
        
        messages.success(request, f'Lead successfully converted to client: {client.name}')
        return redirect('clients:client_detail', pk=client.pk)
        
    except Exception as e:
        messages.error(request, f'Error converting lead to client: {str(e)}')
        return redirect('leads:lead_detail', pk=pk)

@login_required
def lead_dashboard(request):
    # Get overall lead statistics
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    qualified_leads = Lead.objects.filter(status='qualified').count()
    won_leads = Lead.objects.filter(status='won').count()

    # Get leads by status
    status_stats = Lead.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Get leads by source
    source_stats = Lead.objects.values('source').annotate(
        count=Count('id')
    ).order_by('source')

    # Get leads by priority
    priority_stats = Lead.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    # Get recent leads
    recent_leads = Lead.objects.order_by('-created_at')[:5]

    # Get upcoming follow-ups
    upcoming_followups = Lead.objects.filter(
        follow_up_date__isnull=False,
        follow_up_date__gte=timezone.now()
    ).order_by('follow_up_date')[:5]

    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'qualified_leads': qualified_leads,
        'won_leads': won_leads,
        'status_stats': status_stats,
        'source_stats': source_stats,
        'priority_stats': priority_stats,
        'recent_leads': recent_leads,
        'upcoming_followups': upcoming_followups,
        'title': 'Lead Dashboard'
    }
    return render(request, 'leads/lead_dashboard.html', context)

@login_required
def activity_toggle(request, pk):
    activity = get_object_or_404(LeadActivity, pk=pk)
    activity.is_completed = not activity.is_completed
    if activity.is_completed:
        activity.completed_at = timezone.now()
    else:
        activity.completed_at = None
    activity.save()
    return JsonResponse({
        'status': 'success',
        'is_completed': activity.is_completed,
        'completed_at': activity.completed_at.strftime('%Y-%m-%d %H:%M:%S') if activity.completed_at else None
    })

class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 10

    def get_queryset(self):
        queryset = Lead.objects.all()
        form = LeadFilterForm(self.request.GET)

        if form.is_valid():
            status = form.cleaned_data.get('status')
            source = form.cleaned_data.get('source')
            priority = form.cleaned_data.get('priority')
            assigned_to = form.cleaned_data.get('assigned_to')
            date_range = form.cleaned_data.get('date_range')
            search = form.cleaned_data.get('search')

            if status:
                queryset = queryset.filter(status=status)
            if source:
                queryset = queryset.filter(source=source)
            if priority:
                queryset = queryset.filter(priority=priority)
            if assigned_to:
                queryset = queryset.filter(assigned_to=assigned_to)
            if search:
                queryset = queryset.filter(
                    Q(company_name__icontains=search) |
                    Q(contact_person__icontains=search) |
                    Q(email__icontains=search) |
                    Q(description__icontains=search)
                )
            
            if date_range:
                today = timezone.now().date()
                if date_range == 'today':
                    queryset = queryset.filter(created_at__date=today)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LeadFilterForm(self.request.GET)
        return context

class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['activity_form'] = LeadActivityForm()
        context['title'] = f'Lead: {self.object.title or self.object.company_name}'
        
        # Explicitly fetch related notes and documents
        context['notes'] = self.object.notes.all()
        context['documents'] = self.object.documents.all()
        context['activities'] = self.object.activities.all()
        
        return context

    def post(self, request, *args, **kwargs):
        lead = self.get_object()
        action = request.POST.get('action', '')
        
        if action == 'add_note':
            note_form = LeadNoteForm(request.POST)
            if note_form.is_valid():
                try:
                    note = note_form.save(commit=False)
                    note.lead = lead
                    note.created_by_id = request.user.id
                    note.save()
                    messages.success(request, 'Note added successfully.')
                    return redirect('leads:lead_detail', pk=lead.pk)
                except Exception as e:
                    print(f"Unexpected error creating note: {e}")
                    messages.error(request, f'Unexpected error: {e}')
            else:
                print("Note Form Validation Errors:")
                for field, errors in note_form.errors.items():
                    print(f"{field}: {errors}")
                messages.error(request, 'Error adding note. Please check the form.')
        
        elif action == 'add_document':
            document_form = LeadDocumentForm(request.POST, request.FILES)
            if document_form.is_valid():
                try:
                    document = document_form.save(commit=False)
                    document.lead = lead
                    document.created_by_id = request.user.id
                    document.save()
                    messages.success(request, 'Document uploaded successfully.')
                    return redirect('leads:lead_detail', pk=lead.pk)
                except Exception as e:
                    print(f"Unexpected error uploading document: {e}")
                    messages.error(request, f'Unexpected error: {e}')
            else:
                print("Document Form Validation Errors:")
                for field, errors in document_form.errors.items():
                    print(f"{field}: {errors}")
                messages.error(request, 'Error uploading document. Please check the form.')
        
        return redirect('leads:lead_detail', pk=lead.pk)

class LeadCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = 'leads/lead_form.html'
    success_url = reverse_lazy('leads:lead_list')
    success_message = "Lead created successfully."

    def form_valid(self, form):
        form.instance.created_by_id = self.request.user.id
        form.instance.modified_by_id = self.request.user.id
        return super().form_valid(form)

class LeadUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = 'leads/lead_form.html'
    success_message = "Lead updated successfully."

    def get_success_url(self):
        return reverse_lazy('leads:lead_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.modified_by_id = self.request.user.id
        return super().form_valid(form)

class LeadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Lead
    template_name = 'leads/lead_confirm_delete.html'
    success_url = reverse_lazy('leads:lead_list')
    permission_required = 'leads.delete_lead'
    success_message = "Lead deleted successfully."

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

class LeadConvertView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'leads.convert_lead'

    def get(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)
        if lead.status != 'won':
            messages.error(request, 'Only won leads can be converted to clients.')
            return redirect('leads:lead_detail', pk=pk)
        return render(request, 'leads/lead_convert.html', {'lead': lead, 'title': f'Convert Lead: {lead.title or lead.company_name}'})

    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)
        if lead.status != 'won':
            messages.error(request, 'Only won leads can be converted to clients.')
            return redirect('leads:lead_detail', pk=pk)
        
        client = lead.convert_to_client()
        messages.success(request, f'Lead successfully converted to client: {client.name}')
        return redirect('clients:detail', pk=client.pk)

class LeadDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'leads/lead_dashboard.html'
    permission_required = 'leads.view_lead_dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date ranges
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get lead statistics
        context['total_leads'] = Lead.objects.count()
        context['new_leads'] = Lead.objects.filter(status='new').count()
        context['qualified_leads'] = Lead.objects.filter(status='qualified').count()
        context['won_leads'] = Lead.objects.filter(status='won').count()
        
        # Get lead status distribution
        status_data = Lead.objects.values('status').annotate(count=Count('id'))
        context['status_labels'] = [item['status'] for item in status_data]
        context['status_data'] = [item['count'] for item in status_data]
        
        # Get lead source distribution
        source_data = Lead.objects.values('source').annotate(count=Count('id'))
        context['source_labels'] = [item['source'] for item in source_data]
        context['source_data'] = [item['count'] for item in source_data]
        
        # Get recent activities
        context['recent_activities'] = LeadActivity.objects.select_related('lead').order_by('-created_at')[:10]
        
        return context

def activity_toggle(request):
    if request.method == 'POST' and request.is_ajax():
        activity_id = request.POST.get('activity_id')
        activity = get_object_or_404(LeadActivity, pk=activity_id)
        activity.is_completed = True
        activity.completed_at = timezone.now()
        activity.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

# Note Views
class LeadNoteListView(LoginRequiredMixin, ListView):
    model = LeadNote
    template_name = 'leads/lead_note_list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        lead_pk = self.kwargs.get('lead_pk')
        return LeadNote.objects.filter(lead_id=lead_pk).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = get_object_or_404(Lead, pk=self.kwargs.get('lead_pk'))
        return context

class LeadNoteCreateView(LoginRequiredMixin, CreateView):
    model = LeadNote
    form_class = LeadNoteForm
    template_name = 'leads/lead_note_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = get_object_or_404(Lead, pk=self.kwargs.get('lead_pk'))
        return context

    def form_valid(self, form):
        lead = get_object_or_404(Lead, pk=self.kwargs.get('lead_pk'))
        form.instance.lead = lead
        form.instance.created_by_id = self.request.user.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('leads:lead_note_list', kwargs={'lead_pk': self.kwargs.get('lead_pk')})

class LeadNoteDetailView(LoginRequiredMixin, DetailView):
    model = LeadNote
    template_name = 'leads/lead_note_detail.html'
    context_object_name = 'note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.object.lead
        return context

class LeadNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = LeadNote
    form_class = LeadNoteForm
    template_name = 'leads/lead_note_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.object.lead
        return context

    def get_success_url(self):
        return reverse_lazy('leads:lead_note_list', kwargs={'lead_pk': self.object.lead.pk})

class LeadNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = LeadNote
    template_name = 'leads/lead_note_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.object.lead
        return context

    def get_success_url(self):
        return reverse_lazy('leads:lead_note_list', kwargs={'lead_pk': self.object.lead.pk})

# Document Views
class LeadDocumentListView(LoginRequiredMixin, ListView):
    model = LeadDocument
    template_name = 'leads/lead_document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        lead_pk = self.kwargs.get('lead_pk')
        return LeadDocument.objects.filter(lead_id=lead_pk).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = get_object_or_404(Lead, pk=self.kwargs.get('lead_pk'))
        return context

class LeadDocumentCreateView(LoginRequiredMixin, CreateView):
    model = LeadDocument
    form_class = LeadDocumentForm
    template_name = 'leads/lead_document_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = get_object_or_404(Lead, pk=self.kwargs.get('lead_pk'))
        return context

    def form_valid(self, form):
        lead = get_object_or_404(Lead, pk=self.kwargs.get('lead_pk'))
        form.instance.lead = lead
        form.instance.created_by_id = self.request.user.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('leads:lead_document_list', kwargs={'lead_pk': self.kwargs.get('lead_pk')})

class LeadDocumentDetailView(LoginRequiredMixin, DetailView):
    model = LeadDocument
    template_name = 'leads/lead_document_detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.object.lead
        return context

class LeadDocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = LeadDocument
    form_class = LeadDocumentForm
    template_name = 'leads/lead_document_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.object.lead
        return context

    def get_success_url(self):
        return reverse_lazy('leads:lead_document_list', kwargs={'lead_pk': self.object.lead.pk})

class LeadDocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = LeadDocument
    template_name = 'leads/lead_document_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lead'] = self.object.lead
        return context

    def get_success_url(self):
        return reverse_lazy('leads:lead_document_list', kwargs={'lead_pk': self.object.lead.pk})

@login_required
def lead_detail_custom(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    notes = lead.notes.all().order_by('-created_at')
    documents = lead.documents.all().order_by('-created_at')
    activities = lead.activities.all().order_by('-created_at')
    
    context = {
        'lead': lead,
        'notes': notes,
        'documents': documents,
        'activities': activities,
        'page_title': f"{lead.contact_person} | {lead.company_name}"
    }
    
    return render(request, 'leads/lead_detail.html', context)

@login_required
def add_note(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            note = LeadNote.objects.create(
                lead=lead,
                content=content,
                created_by_id=request.user.id
            )
            
            # Create activity record
            LeadActivity.objects.create(
                lead=lead,
                activity_type='note',
                description=f"Added a new note",
                created_by_id=request.user.id
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'content': note.content,
                    'created_by': request.user.username,
                    'created_at': note.created_at.strftime('%b %d, %Y %H:%M')
                })
            
            messages.success(request, "Note added successfully.")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'content': 'Note content is required.'}
                })
            
            messages.error(request, "Note content is required.")
    
    return redirect('leads:lead_detail_custom', pk=lead.pk)

@login_required
def add_document(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        file = request.FILES.get('file')
        
        if file:
            document = LeadDocument.objects.create(
                lead=lead,
                file=file,
                description=description,
                created_by_id=request.user.id
            )
            
            # Create activity record
            LeadActivity.objects.create(
                lead=lead,
                activity_type='document',
                description=f"Uploaded document: {file.name}",
                created_by_id=request.user.id
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'file_name': document.file.name,
                    'file_url': document.file.url,
                    'description': document.description,
                    'created_by': request.user.username,
                    'created_at': document.created_at.strftime('%b %d, %Y')
                })
            
            messages.success(request, "Document uploaded successfully.")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'file': 'File is required.'}
                })
            
            messages.error(request, "File is required.")
    
    return redirect('leads:lead_detail_custom', pk=lead.pk)

@login_required
def delete_note(request, pk):
    note = get_object_or_404(LeadNote, pk=pk)
    lead = note.lead
    
    # Check if the user is authorized to delete this note
    if note.created_by_id == request.user.id:
        note.delete()
        
        # Create activity record
        LeadActivity.objects.create(
            lead=lead,
            activity_type='note',
            description=f"Deleted a note",
            created_by_id=request.user.id
        )
        
        messages.success(request, "Note deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this note.")
    
    return redirect('leads:lead_detail_custom', pk=lead.pk)

@login_required
def delete_document(request, pk):
    document = get_object_or_404(LeadDocument, pk=pk)
    lead = document.lead
    
    # Check if the user is authorized to delete this document
    if document.created_by == request.user:
        document.delete()
        
        # Create activity record
        LeadActivity.objects.create(
            lead=lead,
            activity_type='note',
            description=f"Deleted document: {document.file.name}",
            created_by=request.user
        )
        
        messages.success(request, "Document deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this document.")
    
    return redirect('leads:lead_detail_custom', pk=lead.pk)
