def profile_context(request):
    """
    Add profile to template context if it exists in request
    """
    return {
        'profile': getattr(request, 'profile', None)
    } 