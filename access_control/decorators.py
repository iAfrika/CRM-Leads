from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve

from .models import View, Permission

def check_view_permission(view_func):
    """
    Decorator to check if a user has permission to access a view.
    This is useful for views that need explicit permission checks
    beyond the middleware.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)

        try:
            # Get view information
            view_name = view_func.__name__
            app_name = view_func.__module__.split('.')[0]

            # Check permission
            view = View.objects.get(
                app_name=app_name,
                view_name=view_name
            )
            has_permission = Permission.objects.filter(
                user=request.user,
                view=view,
                is_active=True
            ).exists()

            if has_permission:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request,
                    "You don't have permission to access this page."
                )
                return redirect('home')

        except View.DoesNotExist:
            # Create the view if it doesn't exist
            View.objects.create(
                app_name=app_name,
                view_name=view_name,
                url_pattern=request.path_info
            )
            messages.error(
                request,
                "Access to this page is restricted. Please contact an administrator."
            )
            return redirect('home')

    return wrapper 