from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages
from django.conf import settings

from .models import View, Permission

class ViewPermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._exempt_urls = getattr(settings, 'PERMISSION_EXEMPT_URLS', [])
        self._exempt_paths = getattr(settings, 'PERMISSION_EXEMPT_PATHS', [
            '/admin/',
            '/login/',
            '/logout/',
            '/access-control/',
        ])

    def __call__(self, request):
        # Skip middleware for exempt URLs and paths
        path = request.path_info.lstrip('/')
        if any(path.startswith(url.lstrip('/')) for url in self._exempt_paths):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        # Get the current view
        try:
            resolved = resolve(request.path_info)
            view_name = resolved.func.__name__
            app_name = resolved.func.__module__.split('.')[0]

            # Check if view exists and user has permission
            try:
                view = View.objects.get(
                    app_name=app_name,
                    view_name=view_name
                )
                has_permission = Permission.objects.filter(
                    user=request.user,
                    view=view,
                    is_active=True
                ).exists()

                if not has_permission:
                    messages.error(
                        request,
                        f"You don't have permission to access this page."
                    )
                    return redirect('home')  # Redirect to your home page

            except View.DoesNotExist:
                # If view doesn't exist in our system, we'll create it
                # This helps with dynamic view discovery
                View.objects.create(
                    app_name=app_name,
                    view_name=view_name,
                    url_pattern=request.path_info
                )
                # By default, deny access to newly discovered views
                messages.error(
                    request,
                    f"Access to this page is restricted. Please contact an administrator."
                )
                return redirect('home')

        except (ValueError, AttributeError):
            # If we can't resolve the view, let it pass through
            # This handles cases like static files
            pass

        return self.get_response(request) 