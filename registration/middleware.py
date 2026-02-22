from django.shortcuts import redirect
from django.urls import reverse
from .models import CompanyUser, CompanyApp
from .company_database import set_active_company_database


class CompanyContextMiddleware:
    """
    Middleware to automatically set the active company context for authenticated users.
    This middleware:
    - Retrieves the active company from the session
    - If no active company is set, selects the user's first company
    - Attaches company information to the request object
    - Redirects to registration if user has no company
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only process for authenticated users
        if request.user.is_authenticated:
            # Skip middleware for certain paths
            excluded_paths = ['/auth/', '/registration/', '/admin/', '/static/', '/media/']
            if not any(request.path.startswith(path) for path in excluded_paths):
                # Get active company from session
                active_company_id = request.session.get('active_company_id')
                
                if not active_company_id:
                    # Try to get user's first company
                    try:
                        company_user = CompanyUser.objects.filter(user=request.user).select_related('company').first()
                        if company_user:
                            # Set the active company in session
                            request.session['active_company_id'] = company_user.company.id
                            request.session['active_company_name'] = company_user.company.name
                            request.session['user_role'] = company_user.role
                            active_company_id = company_user.company.id
                        else:
                            # User has no company - redirect to registration
                            if not request.path.startswith('/registration/'):
                                return redirect(reverse('registration:registration_home'))
                    except Exception:
                        pass
                
                # Attach company context to request
                if active_company_id:
                    try:
                        company_user = CompanyUser.objects.select_related('company').get(
                            user=request.user,
                            company_id=active_company_id
                        )
                        request.company = company_user.company
                        request.company_id = company_user.company.id
                        request.user_role = company_user.role
                        
                        # Switch to company-specific database
                        set_active_company_database(company_user.company)
                        
                        # Attach enabled apps list to request
                        enabled_apps = CompanyApp.objects.filter(
                            company=company_user.company,
                            is_enabled=True,
                            app_module__is_active=True
                        ).values_list('app_module__name', flat=True)
                        request.enabled_apps = list(enabled_apps)
                        
                    except CompanyUser.DoesNotExist:
                        # Company no longer exists or user removed - clear session
                        request.session.pop('active_company_id', None)
                        request.session.pop('active_company_name', None)
                        request.session.pop('user_role', None)
                        set_active_company_database(None)
                else:
                    set_active_company_database(None)
        
        response = self.get_response(request)
        return response
