#!/usr/bin/env python

"""
Create leads app for CRM-Leads project
"""

import os
import sys
import subprocess

def run_command(command):
    """Run a command and return its output"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(f"Error: {stderr.decode('utf-8')}")
        return False
    return stdout.decode('utf-8')

def create_leads_app():
    """Create leads app"""
    print("Creating leads app...")
    
    # Check if Django is installed
    try:
        import django
        print(f"Django version: {django.get_version()}")
    except ImportError:
        print("Django is not installed. Please install Django first.")
        return False
    
    # Create leads app
    if not os.path.exists('leads'):
        print("Creating leads app...")
        create_app = run_command('python manage.py startapp leads')
        if not create_app:
            print("Could not create leads app.")
            return False
    else:
        print("Leads app already exists.")
    
    # Create models.py
    print("Creating models.py...")
    models_content = """from django.db import models
from django.conf import settings
from django.utils import timezone


class LeadStatus(models.TextChoices):
    NEW = 'NEW', 'New'
    CONTACTED = 'CONTACTED', 'Contacted'
    QUALIFIED = 'QUALIFIED', 'Qualified'
    PROPOSAL = 'PROPOSAL', 'Proposal'
    NEGOTIATION = 'NEGOTIATION', 'Negotiation'
    WON = 'WON', 'Won'
    LOST = 'LOST', 'Lost'


class LeadSource(models.TextChoices):
    WEBSITE = 'WEBSITE', 'Website'
    REFERRAL = 'REFERRAL', 'Referral'
    EMAIL = 'EMAIL', 'Email Campaign'
    SOCIAL = 'SOCIAL', 'Social Media'
    CALL = 'CALL', 'Cold Call'
    OTHER = 'OTHER', 'Other'


class Lead(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW
    )
    source = models.CharField(
        max_length=20,
        choices=LeadSource.choices,
        default=LeadSource.OTHER
    )
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Activity(models.Model):
    class ActivityType(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        CALL = 'CALL', 'Phone Call'
        MEETING = 'MEETING', 'Meeting'
        NOTE = 'NOTE', 'Note'
        OTHER = 'OTHER', 'Other'
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        default=ActivityType.NOTE
    )
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities'
    )
    performed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_activity_type_display()}: {self.subject}"
    
    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['-performed_at']
"""
    with open(os.path.join('leads', 'models.py'), 'w') as f:
        f.write(models_content)
    
    # Create admin.py
    print("Creating admin.py...")
    admin_content = """from django.contrib import admin
from .models import Lead, Activity


class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 0


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'status', 'source', 'assigned_to', 'created_at')
    list_filter = ('status', 'source', 'created_at', 'assigned_to')
    search_fields = ('name', 'company', 'email', 'description')
    inlines = [ActivityInline]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('subject', 'activity_type', 'lead', 'performed_by', 'performed_at')
    list_filter = ('activity_type', 'performed_at', 'performed_by')
    search_fields = ('subject', 'description', 'lead__name')
"""
    with open(os.path.join('leads', 'admin.py'), 'w') as f:
        f.write(admin_content)
    
    # Create forms.py
    print("Creating forms.py...")
    forms_content = """from django import forms
from .models import Lead, Activity


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'company', 'email', 'phone', 'status', 'source', 'description', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['activity_type', 'subject', 'description', 'performed_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'performed_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
"""
    with open(os.path.join('leads', 'forms.py'), 'w') as f:
        f.write(forms_content)
    
    # Create views.py
    print("Creating views.py...")
    views_content = """from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Lead, Activity
from .forms import LeadForm, ActivityForm


@login_required
def lead_list(request):
    leads = Lead.objects.all()
    return render(request, 'leads/lead_list.html', {'leads': leads})


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    activities = lead.activities.all()
    
    # Handle activity form
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.lead = lead
            activity.performed_by = request.user
            activity.save()
            messages.success(request, 'Activity added successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = ActivityForm(initial={'performed_at': timezone.now()})
    
    return render(request, 'leads/lead_detail.html', {
        'lead': lead,
        'activities': activities,
        'form': form
    })


@login_required
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            messages.success(request, 'Lead created successfully.')
            return redirect('leads:lead_detail', pk=lead.pk)
    else:
        form = LeadForm(initial={'assigned_to': request.user})
    
    return render(request, 'leads/lead_form.html', {'form': form, 'title': 'Create Lead'})


@login_required
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
    
    return render(request, 'leads/lead_form.html', {'form': form, 'lead': lead, 'title': 'Update Lead'})


@login_required
def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully.')
        return redirect('leads:lead_list')
    
    return render(request, 'leads/lead_confirm_delete.html', {'lead': lead})
"""
    with open(os.path.join('leads', 'views.py'), 'w') as f:
        f.write(views_content)
    
    # Create URLs
    print("Creating urls.py...")
    urls_content = """from django.urls import path
from . import views

app_name = 'leads'

urlpatterns = [
    path('', views.lead_list, name='lead_list'),
    path('<int:pk>/', views.lead_detail, name='lead_detail'),
    path('create/', views.lead_create, name='lead_create'),
    path('<int:pk>/update/', views.lead_update, name='lead_update'),
    path('<int:pk>/delete/', views.lead_delete, name='lead_delete'),
]
"""
    with open(os.path.join('leads', 'urls.py'), 'w') as f:
        f.write(urls_content)
    
    # Create templates directory
    templates_dir = os.path.join('leads', 'templates', 'leads')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create base template
    print("Creating templates...")
    base_template = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CRM Leads{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'leads:lead_list' %}">CRM Leads</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'leads:lead_list' %}">Leads</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'leads:lead_create' %}">New Lead</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <span class="nav-link">{{ user.username }}</span>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'admin:logout' %}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'admin:login' %}">Login</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4 mb-5">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
"""
    with open(os.path.join(templates_dir, 'base.html'), 'w') as f:
        f.write(base_template)
    
    # Create lead list template
    lead_list_template = """{% extends 'leads/base.html' %}

{% block title %}Leads | CRM Leads{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h1>Leads</h1>
    </div>
    <div class="col-auto">
        <a href="{% url 'leads:lead_create' %}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> New Lead
        </a>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Company</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Source</th>
                        <th>Assigned To</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lead in leads %}
                    <tr>
                        <td>
                            <a href="{% url 'leads:lead_detail' lead.pk %}">{{ lead.name }}</a>
                        </td>
                        <td>{{ lead.company|default:"-" }}</td>
                        <td>{{ lead.email }}</td>
                        <td>
                            <span class="badge 
                                {% if lead.status == 'NEW' %}bg-info
                                {% elif lead.status == 'CONTACTED' %}bg-primary
                                {% elif lead.status == 'QUALIFIED' %}bg-success
                                {% elif lead.status == 'PROPOSAL' %}bg-warning
                                {% elif lead.status == 'NEGOTIATION' %}bg-warning
                                {% elif lead.status == 'WON' %}bg-success
                                {% elif lead.status == 'LOST' %}bg-danger
                                {% endif %}">
                                {{ lead.get_status_display }}
                            </span>
                        </td>
                        <td>{{ lead.get_source_display }}</td>
                        <td>{{ lead.assigned_to|default:"-" }}</td>
                        <td>{{ lead.created_at|date:"M d, Y" }}</td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <a href="{% url 'leads:lead_detail' lead.pk %}" class="btn btn-outline-primary">
                                    <i class="bi bi-eye"></i>
                                </a>
                                <a href="{% url 'leads:lead_update' lead.pk %}" class="btn btn-outline-secondary">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <a href="{% url 'leads:lead_delete' lead.pk %}" class="btn btn-outline-danger">
                                    <i class="bi bi-trash"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="8" class="text-center">No leads found</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
"""
    with open(os.path.join(templates_dir, 'lead_list.html'), 'w') as f:
        f.write(lead_list_template)
    
    # Create lead detail template
    lead_detail_template = """{% extends 'leads/base.html' %}

{% block title %}{{ lead.name }} | CRM Leads{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h1>{{ lead.name }}</h1>
    </div>
    <div class="col-auto">
        <div class="btn-group">
            <a href="{% url 'leads:lead_update' lead.pk %}" class="btn btn-primary">
                <i class="bi bi-pencil"></i> Edit
            </a>
            <a href="{% url 'leads:lead_delete' lead.pk %}" class="btn btn-danger">
                <i class="bi bi-trash"></i> Delete
            </a>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Lead Details</h5>
                <span class="badge 
                    {% if lead.status == 'NEW' %}bg-info
                    {% elif lead.status == 'CONTACTED' %}bg-primary
                    {% elif lead.status == 'QUALIFIED' %}bg-success
                    {% elif lead.status == 'PROPOSAL' %}bg-warning
                    {% elif lead.status == 'NEGOTIATION' %}bg-warning
                    {% elif lead.status == 'WON' %}bg-success
                    {% elif lead.status == 'LOST' %}bg-danger
                    {% endif %}">
                    {{ lead.get_status_display }}
                </span>
            </div>
            <div class="card-body">
                <dl class="row">
                    <dt class="col-sm-3">Company</dt>
                    <dd class="col-sm-9">{{ lead.company|default:"-" }}</dd>
                    
                    <dt class="col-sm-3">Email</dt>
                    <dd class="col-sm-9">{{ lead.email }}</dd>
                    
                    <dt class="col-sm-3">Phone</dt>
                    <dd class="col-sm-9">{{ lead.phone|default:"-" }}</dd>
                    
                    <dt class="col-sm-3">Source</dt>
                    <dd class="col-sm-9">{{ lead.get_source_display }}</dd>
                    
                    <dt class="col-sm-3">Assigned To</dt>
                    <dd class="col-sm-9">{{ lead.assigned_to|default:"-" }}</dd>
                    
                    <dt class="col-sm-3">Created</dt>
                    <dd class="col-sm-9">{{ lead.created_at|date:"F d, Y H:i" }}</dd>
                    
                    <dt class="col-sm-3">Last Updated</dt>
                    <dd class="col-sm-9">{{ lead.updated_at|date:"F d, Y H:i" }}</dd>
                    
                    {% if lead.description %}
                    <dt class="col-sm-3">Description</dt>
                    <dd class="col-sm-9">{{ lead.description|linebreaksbr }}</dd>
                    {% endif %}
                </dl>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Activities</h5>
            </div>
            <div class="card-body">
                <div class="timeline">
                    {% for activity in activities %}
                    <div class="card mb-3">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div>
                                <span class="badge 
                                    {% if activity.activity_type == 'EMAIL' %}bg-info
                                    {% elif activity.activity_type == 'CALL' %}bg-primary
                                    {% elif activity.activity_type == 'MEETING' %}bg-success
                                    {% elif activity.activity_type == 'NOTE' %}bg-secondary
                                    {% elif activity.activity_type == 'OTHER' %}bg-dark
                                    {% endif %}">
                                    {{ activity.get_activity_type_display }}
                                </span>
                                <span class="ms-2">{{ activity.subject }}</span>
                            </div>
                            <small class="text-muted">{{ activity.performed_at|date:"F d, Y H:i" }}</small>
                        </div>
                        <div class="card-body">
                            {% if activity.description %}
                            <p>{{ activity.description|linebreaksbr }}</p>
                            {% endif %}
                            <small class="text-muted">
                                By {{ activity.performed_by|default:"Unknown" }}
                            </small>
                        </div>
                    </div>
                    {% empty %}
                    <p class="text-center">No activities recorded yet</p>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">Add Activity</h5>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="{{ form.activity_type.id_for_label }}" class="form-label">Type</label>
                        {{ form.activity_type }}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.subject.id_for_label }}" class="form-label">Subject</label>
                        {{ form.subject }}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.description.id_for_label }}" class="form-label">Description</label>
                        {{ form.description }}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.performed_at.id_for_label }}" class="form-label">Date/Time</label>
                        {{ form.performed_at }}
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Add Activity</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Add Bootstrap classes to form fields
    document.addEventListener('DOMContentLoaded', function() {
        const formFields = document.querySelectorAll('form input, form select, form textarea');
        formFields.forEach(field => {
            field.classList.add('form-control');
        });
    });
</script>
{% endblock %}
"""
    with open(os.path.join(templates_dir, 'lead_detail.html'), 'w') as f:
        f.write(lead_detail_template)
    
    # Create lead form template
    lead_form_template = """{% extends 'leads/base.html' %}

{% block title %}{{ title }} | CRM Leads{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h1>{{ title }}</h1>
    </div>
    <div class="col-auto">
        <a href="{% url 'leads:lead_list' %}" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Back to Leads
        </a>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <form method="post">
            {% csrf_token %}
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <label for="{{ form.name.id_for_label }}" class="form-label">Name*</label>
                    {{ form.name }}
                    {% if form.name.errors %}
                    <div class="text-danger">{{ form.name.errors }}</div>
                    {% endif %}
                </div>
                <div class="col-md-6">
                    <label for="{{ form.company.id_for_label }}" class="form-label">Company</label>
                    {{ form.company }}
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <label for="{{ form.email.id_for_label }}" class="form-label">Email*</label>
                    {{ form.email }}
                    {% if form.email.errors %}
                    <div class="text-danger">{{ form.email.errors }}</div>
                    {% endif %}
                </div>
                <div class="col-md-6">
                    <label for="{{ form.phone.id_for_label }}" class="form-label">Phone</label>
                    {{ form.phone }}
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <label for="{{ form.status.id_for_label }}" class="form-label">Status</label>
                    {{ form.status }}
                </div>
                <div class="col-md-6">
                    <label for="{{ form.source.id_for_label }}" class="form-label">Source</label>
                    {{ form.source }}
                </div>
            </div>
            
            <div class="mb-3">
                <label for="{{ form.assigned_to.id_for_label }}" class="form-label">Assigned To</label>
                {{ form.assigned_to }}
            </div>
            
            <div class="mb-3">
                <label for="{{ form.description.id_for_label }}" class="form-label">Description</label>
                {{ form.description }}
            </div>
            
            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <a href="{% url 'leads:lead_list' %}" class="btn btn-secondary">Cancel</a>
                <button type="submit" class="btn btn-primary">Save</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Add Bootstrap classes to form fields
    document.addEventListener('DOMContentLoaded', function() {
        const formFields = document.querySelectorAll('form input, form select, form textarea');
        formFields.forEach(field => {
            field.classList.add('form-control');
        });
    });
</script>
{% endblock %}
"""
    with open(os.path.join(templates_dir, 'lead_form.html'), 'w') as f:
        f.write(lead_form_template)
    
    # Create lead delete confirmation template
    lead_delete_template = """{% extends 'leads/base.html' %}

{% block title %}Delete {{ lead.name }} | CRM Leads{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h1>Delete Lead</h1>
    </div>
</div>

<div class="card">
    <div class="card-body">
        <p class="mb-4">Are you sure you want to delete the lead <strong>{{ lead.name }}</strong>?</p>
        <p class="text-danger">This action cannot be undone. All activities associated with this lead will also be deleted.</p>
        
        <form method="post">
            {% csrf_token %}
            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <a href="{% url 'leads:lead_detail' lead.pk %}" class="btn btn-secondary">Cancel</a>
                <button type="submit" class="btn btn-danger">Delete</button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
"""
    with open(os.path.join(templates_dir, 'lead_confirm_delete.html'), 'w') as f:
        f.write(lead_delete_template)
    
    # Update project URLs
    print("Updating project URLs...")
    try:
        urls_path = os.path.join('crm_leads', 'urls.py')
        
        if os.path.exists(urls_path):
            with open(urls_path, 'r') as f:
                urls_content = f.read()
            
            # Check if leads.urls is already included
            if "'leads.urls'" not in urls_content and '"leads.urls"' not in urls_content:
                # Add leads URL pattern
                new_url_line = "    path('leads/', include('leads.urls')),"
                
                # Find where to insert the new URL pattern
                if "urlpatterns = [" in urls_content:
                    updated_urls = urls_content.replace(
                        "urlpatterns = [",
                        "urlpatterns = [\n" + new_url_line
                    )
                    
                    # Make sure to import 'include'
                    if "from django.urls import path, include" not in urls_content:
                        if "from django.urls import path" in urls_content:
                            updated_urls = updated_urls.replace(
                                "from django.urls import path",
                                "from django.urls import path, include"
                            )
                    
                    # Write the updated content back to the file
                    with open(urls_path, 'w') as f:
                        f.write(updated_urls)
                    
                    print("Updated project URLs.")
                else:
                    print("Could not find urlpatterns in urls.py")
            else:
                print("Leads URLs already included in project urls.py")
        else:
            print(f"URLs file not found at {urls_path}")
    
    except Exception as e:
        print(f"Error updating project URLs: {str(e)}")
    
    print("\nLeads app created successfully!")
    print("\nNext steps:")
    print("1. Run 'python manage.py makemigrations leads' to create lead migrations")
    print("2. Run 'python manage.py migrate_schemas' to apply all migrations")
    print("3. Run 'python manage.py runserver' to start the development server")
    
    return True

if __name__ == "__main__":
    create_leads_app() 