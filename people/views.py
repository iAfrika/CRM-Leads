from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Person, Role, ContactHistory
from .forms import PersonForm, RoleAssignmentForm, ContactForm
from .services.telegram_service import TelegramService
from .services.email_service import EmailService
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import os

# Create your views here.
@login_required
def register_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            person = form.save(commit=False)
            person.registered_by_id = request.user.id
            person.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f"{person.full_name} has been registered successfully.")
            return redirect('people:person_detail', pk=person.pk)
        
    else:
        form = PersonForm()

    return render(request, 'people/register.html', {'form': form})

@login_required
def people_list(request):
    """List all people with search and pagination"""
    name_filter = request.GET.get('name', '')
    email_filter = request.GET.get('email', '')
    role_filter = request.GET.get('role', '')

    # Filter people based on search and role
    people = Person.objects.all()
    if name_filter:
        people = people.filter(
            Q(first_name__icontains=name_filter) | 
            Q(last_name__icontains=name_filter)
        )
    if email_filter:
        people = people.filter(email__icontains=email_filter)
    if role_filter:
        people = people.filter(role__id=role_filter)

    # Get all roles for filtering
    roles = Role.objects.all()

    # Pagination
    paginator = Paginator(people, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'people/people_list.html', {
        'people': page_obj,  # Pass the page_obj as people
        'page_obj': page_obj,
        'roles': roles,
        'name_filter': name_filter,
        'email_filter': email_filter,
        'role_filter': role_filter,
    })

@login_required
def person_detail(request, pk):
    """View to display detailed information about a person"""
    person = get_object_or_404(Person, pk=pk)
    
    if request.method == 'POST' and 'assign_roles' in request.POST:
        role_form = RoleAssignmentForm(request.POST, instance=person)
        if role_form.is_valid():
            role_form.save()
            messages.success(request, 'Roles assigned successfully.')
            return redirect('people:person_detail', pk=person.pk)
    
    role_form = RoleAssignmentForm(instance=person)

    return render(request, 'people/person_detail.html', {
        'person': person,
        'role_form': role_form,
        'contact_history': person.contact_history.all()[:10], # Last 10 contact history
    })

@login_required
def contact_people(request):
    """View to manage contact history"""
    if request.method == 'POST':
        form=ContactForm(request.POST)
        if form.is_valid():
            contact_type = form.cleaned_data['contact_type']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipients = form.cleaned_data['recipients']

            success_count = 0
            error_messages = []

            # Process each recipient
            for person in recipients:
                contact_history = ContactHistory(
                    person=person,
                    contact_type=contact_type,
                    subject=subject,
                    message=message,
                    sent_by=request.user,
                )

                #Send message based on content type
                if contact_type == 'email' and person.email:
                    email_service = EmailService()
                    success, error = email_service.send_email(subject, message, person.email)
                    if success:
                        success_count += 1
                        contact_history.save()
                    else:
                        error_messages.append(f"Failed to send email to {person.full_name}: {error}")

                elif contact_type == 'telegram' and person.telegram_username:
                    telegram_service = TelegramService()
                    success, error = telegram_service.send_message(message, person.telegram_username)
                    if success:
                        success_count += 1
                        contact_history.save()
                    else:
                        error_messages.append(f"Failed to send telegram message to {person.full_name}: {error}")

                else:
                    error_messages.append(f"No {'email' if contact_type == 'email' else 'Telegram username'} info for {person.full_name}")
                
                # Display results
                if success_count > 0:
                    messages.success(request, f"Successfully sent {contact_type} to {success_count} recipients.")

                if error_messages:
                    for error in error_messages:
                        messages.error(request, error)

                return redirect('people:people_list')

    else:
        form = ContactForm()

    return render(request, 'people/contact_form.html', {'form': form})

@login_required
def update_person(request, pk):
    """View to update a person's information"""
    person = get_object_or_404(Person, pk=pk)
    
    if request.method == 'POST':
        form = PersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, f"{person.full_name}'s information has been updated successfully.")
            return redirect('people:person_detail', pk=person.pk)
    else:
        form = PersonForm(instance=person)
    
    return render(request, 'people/register.html', {
        'form': form,
        'person': person,
        'is_update': True
    })

@login_required
@require_POST
@csrf_protect
def delete_person(request, pk):
    """
    Delete a person record.
    
    This view handles the deletion of a person record with soft delete 
    or hard delete based on system configuration.
    """
    try:
        person = get_object_or_404(Person, pk=pk)
        
        # Optional: Add permission check
        if not request.user.is_staff and not request.user.is_superuser:
            return JsonResponse({
                'status': 'error', 
                'message': 'You do not have permission to delete people.'
            }, status=403)
        
        # Soft delete or hard delete based on configuration
        if getattr(settings, 'SOFT_DELETE_ENABLED', False):
            # Soft delete: mark as inactive
            person.is_active = False
            person.save()
        else:
            # Hard delete
            person.delete()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'{person.full_name} has been deleted successfully.'
        })
    
    except Person.DoesNotExist:
        return JsonResponse({
            'status': 'error', 
            'message': 'Person not found.'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=500)

# Add a debug view to check static files
def debug_static(request):
    """Debug view to check static file paths"""
    static_root = settings.STATIC_ROOT
    static_url = settings.STATIC_URL
    
    people_css_path = os.path.join(settings.BASE_DIR, 'people', 'static', 'people', 'css')
    people_css_files = []
    if os.path.exists(people_css_path):
        people_css_files = os.listdir(people_css_path)
    
    collected_path = None
    collected_files = []
    if static_root and os.path.exists(static_root):
        collected_path = os.path.join(static_root, 'people', 'css')
        if os.path.exists(collected_path):
            collected_files = os.listdir(collected_path)
    
    output = f"""
    <h1>Static Files Debug</h1>
    <h2>Settings</h2>
    <p>STATIC_URL: {static_url}</p>
    <p>STATIC_ROOT: {static_root}</p>
    
    <h2>People CSS Files (Source)</h2>
    <p>Path: {people_css_path}</p>
    <p>Exists: {os.path.exists(people_css_path)}</p>
    <ul>
    {"".join([f"<li>{f}</li>" for f in people_css_files])}
    </ul>
    
    <h2>Collected CSS Files</h2>
    <p>Path: {collected_path}</p>
    <p>Exists: {collected_path and os.path.exists(collected_path)}</p>
    <ul>
    {"".join([f"<li>{f}</li>" for f in collected_files])}
    </ul>
    """
    
    return HttpResponse(output)
