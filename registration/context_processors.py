from .models import CompanyUser


def company_context(request):
    """
    Context processor to make company information available in all templates.
    Provides:
    - active_company: The currently active company object
    - active_company_id: ID of the active company
    - user_companies: List of all companies the user belongs to
    - user_company_count: Number of companies user belongs to
    - enabled_apps: List of enabled app names for the active company
    """
    context = {
        'active_company': None,
        'active_company_id': None,
        'user_companies': [],
        'user_company_count': 0,
        'enabled_apps': [],
    }
    
    if request.user.is_authenticated:
        # Get active company from request (set by middleware)
        if hasattr(request, 'company'):
            context['active_company'] = request.company
            context['active_company_id'] = request.company.id
        
        # Get enabled apps from request (set by middleware)
        if hasattr(request, 'enabled_apps'):
            context['enabled_apps'] = request.enabled_apps
        
        # Get all companies user belongs to
        user_companies = CompanyUser.objects.filter(
            user=request.user
        ).select_related('company').order_by('company__name')
        
        context['user_companies'] = user_companies
        context['user_company_count'] = user_companies.count()
    
    return context
