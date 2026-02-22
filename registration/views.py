from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import SubscriptionPlan, Company, CompanyUser, AppModule, CompanyApp
from .forms import UserRegistrationForm, CompanyUserAssignmentForm, ExistingUserAssignmentForm, UserInvitationForm, CompanyEditForm, CompanyBankAccountFormSet
from django.utils.text import slugify
from .company_database import create_company_database
import uuid
import os

# Create your views here.

@login_required
def company_selection(request):
    """Company selection page - shown after login"""
    # Get all companies the user has access to
    user_companies = CompanyUser.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('company').order_by('company__name')
    
    # If user has no companies, redirect to registration
    if not user_companies.exists():
        messages.warning(request, "You are not associated with any company. Please register a new company or contact your administrator.")
        return redirect('registration:register_company')
    
    # If user has only one company, automatically select it
    if user_companies.count() == 1:
        return redirect('registration:activate_company', company_id=user_companies.first().company.id)
    
    context = {
        'user_companies': user_companies,
    }
    return render(request, 'registration/company_selection.html', context)


@login_required
def activate_company(request, company_id):
    """Activate a company for the current session"""
    # Verify user has access to this company
    try:
        company_user = CompanyUser.objects.select_related('company').get(
            user=request.user,
            company_id=company_id,
            is_active=True
        )
    except CompanyUser.DoesNotExist:
        messages.error(request, "You don't have access to this company.")
        return redirect('registration:company_selection')
    
    # Set active company in session
    request.session['active_company_id'] = company_user.company.id
    request.session['active_company_name'] = company_user.company.name
    request.session['user_role'] = company_user.role
    
    messages.success(request, f"You are now working with {company_user.company.name}")
    
    # Redirect to dashboard
    return redirect('dashboard:main_dashboard')


def registration_home(request):
    """Registration app home page"""
    return render(request, 'registration/registration_home.html')

def register_company(request):
    """Company registration form"""
    if request.method == 'POST':
        # Process the form submission
        company_name = request.POST.get('company_name')
        initials = request.POST.get('initials', '').upper().strip()
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        tax_pin = request.POST.get('tax_pin', '')
        physical_address = request.POST.get('physical_address')
        postal_address = request.POST.get('postal_address', '')
        
        # Generate a unique database name based on company name
        database_name = f"{slugify(company_name)}_{uuid.uuid4().hex[:8]}"
        
        # Create the company
        company = Company(
            name=company_name,
            initials=initials,
            phone_number=phone_number,
            email=email,
            tax_pin=tax_pin,
            physical_address=physical_address,
            postal_address=postal_address,
            database_name=database_name
        )
        
        # Handle logo upload if provided
        if 'company_logo' in request.FILES:
            company.logo = request.FILES['company_logo']
        
        # Save the company
        company.save()
        
        # Create a separate database for the company
        create_company_database(company)
        
        # If user is authenticated, associate them as admin
        if request.user.is_authenticated:
            CompanyUser.objects.create(
                company=company,
                user=request.user,
                role='admin',
                is_active=True
            )
        
        # Enable default apps for the new company
        enable_default_apps(company, request.user if request.user.is_authenticated else None)
        
        # Add success message
        messages.success(request, f"Company '{company_name}' has been successfully registered with its own database!")
        
        # If user is authenticated, activate the new company
        if request.user.is_authenticated:
            return redirect('registration:activate_company', company_id=company.id)
        else:
            # Redirect to company list
            return redirect('registration:company_list')
    
    # If GET request, just render the form
    return render(request, 'registration/register_company.html')

def register_user(request):
    """User registration form"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Create a profile for the user
            from authentication.models import Profile
            Profile.objects.create(
                user=user, 
                name=f"{user.first_name} {user.last_name}".strip() or user.username
            )
            
            messages.success(request, f"Account for {user.get_full_name() or user.username} has been created successfully!")
            
            # Redirect to login page or company registration
            return redirect('authentication:login')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'registration/register_user.html', context)

def app_selection(request):
    """App selection page"""
    return render(request, 'registration/app_selection.html')

def company_list(request):
    """Company list page"""
    # Get all companies
    companies = Company.objects.all().order_by('-created_at')
    
    context = {
        'companies': companies,
    }
    
    return render(request, 'registration/company_list.html', context)

def company_details(request, company_id=None):
    """Company details page"""
    if company_id:
        # Get specific company
        try:
            company = Company.objects.get(id=company_id)
            context = {'company': company}
            return render(request, 'registration/company_detail.html', context)
        except Company.DoesNotExist:
            messages.error(request, "Company not found")
            return redirect('registration:company_list')
    else:
        # For backward compatibility, show all companies
        # This will eventually be removed after updating all references
        companies = Company.objects.all().order_by('-created_at')
        context = {
            'companies': companies,
        }
        return render(request, 'registration/company_details.html', context)

# Placeholder views to prevent NoReverseMatch errors
def placeholder_subscription_plans(request):
    """Placeholder for subscription plans page"""
    return render(request, 'registration/placeholder.html', {
        'message': 'Subscription plans feature is currently under maintenance.'
    })

@login_required
def company_users(request, company_id):
    """View and manage users for a specific company"""
    company = get_object_or_404(Company, id=company_id)
    
    # Get all users assigned to this company
    company_users = CompanyUser.objects.filter(company=company).select_related('user')
    
    context = {
        'company': company,
        'company_users': company_users,
    }
    
    return render(request, 'registration/company_users.html', context)

@login_required
def register_company_user(request, company_id):
    """Register a new user and assign them to a company"""
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            
            # Create company user association
            role = request.POST.get('role', 'staff')
            notes = request.POST.get('notes', '')
            
            CompanyUser.objects.create(
                company=company,
                user=user,
                role=role,
                notes=notes,
                invited_by=request.user
            )
            
            # Create a profile for the user if it doesn't exist
            from authentication.models import Profile
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user, name=f"{user.first_name} {user.last_name}".strip() or user.username)
            
            messages.success(request, f"User {user.username} has been registered and assigned to {company.name}.")
            return redirect('registration:company_users', company_id=company.id)
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'company': company,
        'roles': CompanyUser.ROLE_CHOICES,
    }
    
    return render(request, 'registration/register_company_user.html', context)

@login_required
def assign_existing_user(request, company_id):
    """Assign an existing user to a company"""
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = ExistingUserAssignmentForm(request.POST)
        if form.is_valid():
            user = form.user  # This is set in the form's clean_email method
            role = form.cleaned_data['role']
            notes = form.cleaned_data.get('notes', '')
            
            # Check if this user is already assigned to this company
            if CompanyUser.objects.filter(company=company, user=user).exists():
                messages.error(request, f"User {user.email} is already assigned to this company.")
            else:
                CompanyUser.objects.create(
                    company=company,
                    user=user,
                    role=role,
                    notes=notes,
                    invited_by=request.user
                )
                
                # Create a profile for the user if it doesn't exist
                from authentication.models import Profile
                if not hasattr(user, 'profile'):
                    Profile.objects.create(user=user, name=f"{user.first_name} {user.last_name}".strip() or user.username)
                
                messages.success(request, f"User {user.email} has been assigned to {company.name} as {dict(CompanyUser.ROLE_CHOICES)[role]}.")
            
            return redirect('registration:company_users', company_id=company.id)
    else:
        form = ExistingUserAssignmentForm()
    
    context = {
        'form': form,
        'company': company,
    }
    
    return render(request, 'registration/assign_existing_user.html', context)

@login_required
def edit_company_user(request, company_id, user_id):
    """Edit a user's role within a company"""
    company = get_object_or_404(Company, id=company_id)
    company_user = get_object_or_404(CompanyUser, company=company, user_id=user_id)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        notes = request.POST.get('notes', '')
        
        company_user.role = role
        company_user.is_active = is_active
        company_user.notes = notes
        company_user.save()
        
        messages.success(request, f"User {company_user.user.email} role has been updated to {company_user.get_role_display()}.")
        return redirect('registration:company_users', company_id=company.id)
    
    context = {
        'company': company,
        'company_user': company_user,
        'roles': CompanyUser.ROLE_CHOICES,
    }
    
    return render(request, 'registration/edit_company_user.html', context)

@login_required
def remove_company_user(request, company_id, user_id):
    """Remove a user from a company"""
    company = get_object_or_404(Company, id=company_id)
    company_user = get_object_or_404(CompanyUser, company=company, user_id=user_id)
    
    if request.method == 'POST':
        username = company_user.user.username
        company_user.delete()
        messages.success(request, f"User {username} has been removed from {company.name}.")
        return redirect('registration:company_users', company_id=company.id)
    
    context = {
        'company': company,
        'company_user': company_user,
    }
    
    return render(request, 'registration/remove_company_user.html', context)

@login_required
def edit_company(request, company_id):
    """Edit company details"""
    company = get_object_or_404(Company, id=company_id)
    
    # Check if user has permission to edit this company
    if not (request.user.is_staff or 
            request.session.get('user_role') == 'admin' or
            company.admin_user == request.user or
            CompanyUser.objects.filter(company=company, user=request.user, role='admin').exists()):
        messages.error(request, "You don't have permission to edit this company.")
        return redirect('registration:company_details', company_id=company_id)
    
    if request.method == 'POST':
        form = CompanyEditForm(request.POST, request.FILES, instance=company)
        bank_formset = CompanyBankAccountFormSet(request.POST, instance=company)
        
        if form.is_valid() and bank_formset.is_valid():
            form.save()
            bank_formset.save()
            messages.success(request, f"Company '{company.name}' and banking information have been successfully updated!")
            return redirect('registration:company_details', company_id=company_id)
        else:
            if not form.is_valid():
                messages.error(request, "Please correct the errors in the company information.")
            if not bank_formset.is_valid():
                messages.error(request, "Please correct the errors in the banking information.")
    else:
        form = CompanyEditForm(instance=company)
        bank_formset = CompanyBankAccountFormSet(instance=company)
    
    context = {
        'form': form,
        'bank_formset': bank_formset,
        'company': company,
    }
    
    return render(request, 'registration/edit_company.html', context)

@login_required
def user_profile(request, company_id, user_id):
    """View detailed user profile and manage user settings"""
    company = get_object_or_404(Company, id=company_id)
    company_user = get_object_or_404(CompanyUser, company=company, user_id=user_id)
    user = company_user.user
    
    # Get user profile if exists
    profile = getattr(user, 'profile', None)
    
    # Get user's other company associations
    other_companies = CompanyUser.objects.filter(user=user).exclude(company=company).select_related('company')
    
    context = {
        'company': company,
        'company_user': company_user,
        'user': user,
        'profile': profile,
        'other_companies': other_companies,
    }
    
    return render(request, 'registration/user_profile.html', context)

@login_required
def edit_user_profile(request, company_id, user_id):
    """Edit user profile information"""
    company = get_object_or_404(Company, id=company_id)
    company_user = get_object_or_404(CompanyUser, company=company, user_id=user_id)
    user = company_user.user
    
    # Check permissions
    if not (request.user.is_staff or 
            request.user == user or
            CompanyUser.objects.filter(company=company, user=request.user, role__in=['admin', 'manager']).exists()):
        messages.error(request, "You don't have permission to edit this user profile.")
        return redirect('registration:user_profile', company_id=company_id, user_id=user_id)
    
    # Get or create profile
    from authentication.models import Profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update user basic info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', user.email)
        
        # Update profile info
        profile.name = request.POST.get('name', '')
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.bio = request.POST.get('bio', '')
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        try:
            user.save()
            profile.save()
            messages.success(request, f"Profile for {user.get_full_name() or user.username} has been updated successfully.")
            return redirect('registration:user_profile', company_id=company_id, user_id=user_id)
        except Exception as e:
            messages.error(request, f"Error updating profile: {str(e)}")
    
    context = {
        'company': company,
        'company_user': company_user,
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'registration/edit_user_profile.html', context)

@login_required
def users_list(request):
    """View all registered users across all companies"""
    # Check if user has admin privileges (Django staff/superuser OR company admin)
    user_is_company_admin = CompanyUser.objects.filter(
        user=request.user, 
        role__in=['admin', 'manager'],
        is_active=True
    ).exists()
    
    if not (request.user.is_staff or request.user.is_superuser or user_is_company_admin):
        messages.error(request, "You don't have permission to view all users.")
        return redirect('registration:registration_home')
    
    # Get all users with their profiles and company associations
    users = User.objects.all().prefetch_related('companyuser_set__company', 'profile').order_by('-date_joined')
    
    # If user is not Django staff but is company admin, limit to their companies' users
    if not (request.user.is_staff or request.user.is_superuser):
        # Get companies where this user is admin/manager
        user_companies = CompanyUser.objects.filter(
            user=request.user, 
            role__in=['admin', 'manager'],
            is_active=True
        ).values_list('company_id', flat=True)
        
        # Filter users to only those in the same companies
        company_user_ids = CompanyUser.objects.filter(
            company_id__in=user_companies
        ).values_list('user_id', flat=True)
        
        users = users.filter(id__in=company_user_ids)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by active status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    context = {
        'users': users,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
    }
    
    return render(request, 'registration/users_list.html', context)


@login_required
def company_apps(request, company_id):
    """
    Manage which apps are enabled for a company
    """
    company = get_object_or_404(Company, id=company_id)
    
    # Check if user has permission to manage this company
    if not (request.user.is_staff or 
            request.session.get('user_role') == 'admin' or
            company.admin_user == request.user or
            CompanyUser.objects.filter(company=company, user=request.user, role='admin').exists()):
        messages.error(request, "You don't have permission to manage apps for this company.")
        return redirect('registration:company_details', company_id=company_id)
    
    # Handle POST request to enable/disable apps
    if request.method == 'POST':
        app_module_id = request.POST.get('app_module_id')
        action = request.POST.get('action')  # 'enable' or 'disable'
        
        try:
            app_module = AppModule.objects.get(id=app_module_id)
            
            if action == 'enable':
                company_app, created = CompanyApp.objects.get_or_create(
                    company=company,
                    app_module=app_module,
                    defaults={
                        'is_enabled': True,
                        'enabled_by': request.user
                    }
                )
                if not created:
                    company_app.is_enabled = True
                    company_app.enabled_by = request.user
                    company_app.save()
                messages.success(request, f"{app_module.display_name} has been enabled for {company.name}.")
            
            elif action == 'disable':
                company_app = CompanyApp.objects.get(company=company, app_module=app_module)
                company_app.is_enabled = False
                company_app.save()
                messages.warning(request, f"{app_module.display_name} has been disabled for {company.name}.")
        
        except AppModule.DoesNotExist:
            messages.error(request, "App module not found.")
        except CompanyApp.DoesNotExist:
            messages.error(request, "This app is not associated with the company.")
        
        return redirect('registration:company_apps', company_id=company_id)
    
    # Get all available app modules
    all_apps = AppModule.objects.filter(is_active=True).order_by('order', 'display_name')
    
    # Get enabled apps for this company
    enabled_app_ids = CompanyApp.objects.filter(
        company=company,
        is_enabled=True
    ).values_list('app_module_id', flat=True)
    
    # Organize apps with their status
    apps_status = []
    for app in all_apps:
        apps_status.append({
            'module': app,
            'is_enabled': app.id in enabled_app_ids,
        })
    
    context = {
        'company': company,
        'apps_status': apps_status,
    }
    
    return render(request, 'registration/company_apps.html', context)


def enable_default_apps(company, user=None):
    """
    Enable default apps for a newly registered company
    """
    default_apps = ['dashboard', 'clients', 'leads', 'sales', 'documents']
    
    for app_name in default_apps:
        try:
            app_module = AppModule.objects.get(name=app_name)
            CompanyApp.objects.get_or_create(
                company=company,
                app_module=app_module,
                defaults={
                    'is_enabled': True,
                    'enabled_by': user
                }
            )
        except AppModule.DoesNotExist:
            continue
