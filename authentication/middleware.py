from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Profile

class ProfileAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = [
            reverse('authentication:login'),
            reverse('authentication:profile_selection'),
            reverse('authentication:profile_select', args=[0]).rsplit('0', 1)[0],  # Base profile select URL
            '/static/',
            '/media/',
            '/admin/',
        ]

    def __call__(self, request):
        # Check if the URL is public (no auth required)
        if request.path in self.public_urls:
            return self.get_response(request)
        
        # If user is not authenticated and trying to access a protected URL
        if not request.user.is_authenticated:
            if request.path not in self.public_urls:
                return redirect('authentication:login')
            return self.get_response(request)
        
        # User is authenticated - get their role and store it if not present
        if 'user_role' not in request.session:
            # Default to 'staff' if no role set
            request.session['user_role'] = 'staff'
            print(f"Setting default role 'staff' for user {request.user}")
        
        # Get the user's role from session
        role = request.session.get('user_role', 'staff')
        
        # Standardize role naming for consistency
        if role == 'admin':
            role = 'administrator'
            request.session['user_role'] = role
            
        print(f"User {request.user} has role: {role}")
        
        # Simple redirect rules:
        # 1. Administrator going to profile? Send them to dashboard
        if role == 'administrator' and request.path == '/auth/profile/':
            print(f"Redirecting administrator from profile to dashboard")
            return redirect('dashboard:main_dashboard')
        
        # 2. Staff going to dashboard? Send them to staff workspace
        if role == 'staff' and request.path == '/dashboard/':
            print(f"Redirecting staff from dashboard to staff workspace")
            return redirect('authentication:staff_workspace')
        
        # Continue with the request
        return self.get_response(request) 