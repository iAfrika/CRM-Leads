from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _

from .models import View, Permission
from .forms import ViewForm, PermissionForm

def is_admin(user):
    """Check if user is an admin"""
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_index(request):
    """Admin dashboard for the access control app"""
    recent_users = User.objects.filter(
        is_superuser=False, 
        is_staff=False,
        access_control_permissions__isnull=False
    ).annotate(
        permission_count=Count('access_control_permissions')
    ).order_by('-permission_count')[:5]
    
    recent_views = View.objects.annotate(
        user_count=Count('user_permissions')
    ).order_by('-user_count')[:5]
    
    recent_permissions = Permission.objects.select_related('user', 'view').order_by('-granted_at')[:5]
    
    # For the recent actions section
    recent_actions = Permission.objects.select_related('user', 'view', 'granted_by').order_by('-granted_at')[:10]
    
    # Get counts for stats
    views_count = View.objects.count()
    users_count = User.objects.filter(
        is_superuser=False, 
        is_staff=False,
        access_control_permissions__isnull=False
    ).count()
    permissions_count = Permission.objects.filter(is_active=True).count()
    
    context = {
        'title': _('Access Control Admin'),
        'recent_users': recent_users,
        'recent_views': recent_views,
        'recent_permissions': recent_permissions,
        'recent_actions': recent_actions,
        'views_count': views_count,
        'users_count': users_count,
        'permissions_count': permissions_count,
    }
    
    return render(request, 'access_control/admin/index.html', context)

@login_required
@user_passes_test(is_admin)
def admin_views(request):
    """List all views in the system"""
    search_query = request.GET.get('q', '')
    ordering = request.GET.get('o', 'name')
    
    views = View.objects.all()
    
    # Apply search if requested
    if search_query:
        views = views.filter(
            Q(name__icontains=search_query) | 
            Q(app_name__icontains=search_query) | 
            Q(view_name__icontains=search_query) |
            Q(url_pattern__icontains=search_query)
        )
    
    # Apply ordering
    if ordering:
        if ordering.startswith('-'):
            views = views.order_by(ordering, 'name')
        else:
            views = views.order_by(ordering, 'name')
    else:
        views = views.order_by('name')
    
    # Annotate with user count
    views = views.annotate(user_count=Count('user_permissions'))
    
    # Paginate
    paginator = Paginator(views, 25)  # Show 25 views per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': _('Views'),
        'views': page_obj,
        'ordering': ordering,
        'search_query': search_query,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'result_count': views.count(),
        'opts': View._meta,
    }
    
    return render(request, 'access_control/admin/view_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_view_detail(request, pk):
    """View details of a specific View"""
    view_obj = get_object_or_404(View, pk=pk)
    
    permissions = Permission.objects.filter(view=view_obj).select_related('user', 'granted_by')
    
    context = {
        'title': f"{view_obj.name}",
        'view_obj': view_obj,
        'permissions': permissions,
        'opts': View._meta,
    }
    
    return render(request, 'access_control/admin/view_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_view_edit(request, pk=None):
    """Edit an existing View or create a new one"""
    if pk:
        view_obj = get_object_or_404(View, pk=pk)
        title = _('Edit View')
    else:
        view_obj = None
        title = _('Add View')
    
    if request.method == 'POST':
        form = ViewForm(request.POST, instance=view_obj)
        if form.is_valid():
            view_obj = form.save()
            if pk:
                messages.success(request, _('View updated successfully.'))
            else:
                messages.success(request, _('View created successfully.'))
            return redirect('access_control:admin_view_detail', pk=view_obj.pk)
    else:
        form = ViewForm(instance=view_obj)
    
    context = {
        'title': title,
        'form': form,
        'view_obj': view_obj,
        'opts': View._meta,
    }
    
    return render(request, 'access_control/admin/view_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_view_delete(request, pk):
    """Delete a View"""
    view_obj = get_object_or_404(View, pk=pk)
    
    if request.method == 'POST' and request.POST.get('post') == 'yes':
        view_obj.delete()
        messages.success(request, _('View deleted successfully.'))
        return redirect('access_control:admin_views')
    
    # Count related objects
    permissions = Permission.objects.filter(view=view_obj)
    
    context = {
        'title': _('Delete View'),
        'object': view_obj,
        'deleted_objects': [_('Permission: %s') % p for p in permissions],
        'model_name': 'view',
        'back_url': reverse('access_control:admin_views'),
        'back_url_name': 'access_control:admin_views',
        'opts': View._meta,
    }
    
    return render(request, 'access_control/admin/delete_confirmation.html', context)

@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """List all users with permissions"""
    search_query = request.GET.get('q', '')
    ordering = request.GET.get('o', 'username')
    
    users = User.objects.filter(is_superuser=False, is_staff=False)
    
    # Apply search if requested
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply ordering
    if ordering:
        if ordering.startswith('-'):
            users = users.order_by(ordering, 'username')
        else:
            users = users.order_by(ordering, 'username')
    else:
        users = users.order_by('username')
    
    # Annotate with permission count
    users = users.annotate(permission_count=Count('access_control_permissions'))
    
    # Paginate
    paginator = Paginator(users, 25)  # Show 25 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': _('Users'),
        'users': page_obj,
        'ordering': ordering,
        'search_query': search_query,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'result_count': users.count(),
        'opts': User._meta,
    }
    
    return render(request, 'access_control/admin/user_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, pk):
    """View details of a specific User's permissions"""
    user_obj = get_object_or_404(User, pk=pk)
    
    permissions = Permission.objects.filter(user=user_obj).select_related('view', 'granted_by')
    
    context = {
        'title': f"{user_obj.username}",
        'user_obj': user_obj,
        'permissions': permissions,
        'opts': User._meta,
    }
    
    return render(request, 'access_control/admin/user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_permissions(request):
    """List all permissions"""
    search_query = request.GET.get('q', '')
    ordering = request.GET.get('o', '-granted_at')
    
    permissions = Permission.objects.select_related('user', 'view', 'granted_by')
    
    # Apply search if requested
    if search_query:
        permissions = permissions.filter(
            Q(user__username__icontains=search_query) | 
            Q(view__name__icontains=search_query) | 
            Q(view__app_name__icontains=search_query) |
            Q(granted_by__username__icontains=search_query)
        )
    
    # Apply ordering
    if ordering:
        if ordering.startswith('-'):
            permissions = permissions.order_by(ordering, '-granted_at')
        else:
            permissions = permissions.order_by(ordering, '-granted_at')
    else:
        permissions = permissions.order_by('-granted_at')
    
    # Paginate
    paginator = Paginator(permissions, 25)  # Show 25 permissions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': _('Permissions'),
        'permissions': page_obj,
        'ordering': ordering,
        'search_query': search_query,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'result_count': permissions.count(),
        'opts': Permission._meta,
    }
    
    return render(request, 'access_control/admin/permission_list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_permission_detail(request, pk):
    """View details of a specific Permission"""
    permission = get_object_or_404(Permission, pk=pk)
    
    context = {
        'title': f"{permission.user.username} - {permission.view.name}",
        'permission': permission,
        'opts': Permission._meta,
    }
    
    return render(request, 'access_control/admin/permission_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_permission_edit(request, pk=None):
    """Edit an existing Permission or create a new one"""
    if pk:
        permission = get_object_or_404(Permission, pk=pk)
        title = _('Edit Permission')
    else:
        permission = None
        title = _('Add Permission')
    
    if request.method == 'POST':
        form = PermissionForm(request.POST, instance=permission)
        if form.is_valid():
            perm = form.save(commit=False)
            if not pk:  # New permission
                perm.granted_by = request.user
            perm.save()
            
            if pk:
                messages.success(request, _('Permission updated successfully.'))
            else:
                messages.success(request, _('Permission created successfully.'))
            return redirect('access_control:admin_permission_detail', pk=perm.pk)
    else:
        form = PermissionForm(instance=permission)
    
    context = {
        'title': title,
        'form': form,
        'permission': permission,
        'opts': Permission._meta,
    }
    
    return render(request, 'access_control/admin/permission_form.html', context)

@login_required
@user_passes_test(is_admin)
def admin_permission_delete(request, pk):
    """Delete a Permission"""
    permission = get_object_or_404(Permission, pk=pk)
    
    if request.method == 'POST' and request.POST.get('post') == 'yes':
        permission.delete()
        messages.success(request, _('Permission deleted successfully.'))
        return redirect('access_control:admin_permissions')
    
    context = {
        'title': _('Delete Permission'),
        'object': permission,
        'deleted_objects': [str(permission)],
        'model_name': 'permission',
        'back_url': reverse('access_control:admin_permissions'),
        'back_url_name': 'access_control:admin_permissions',
        'opts': Permission._meta,
    }
    
    return render(request, 'access_control/admin/delete_confirmation.html', context)

@login_required
@user_passes_test(is_admin)
def admin_permission_toggle(request, pk):
    """Toggle a permission's active status"""
    permission = get_object_or_404(Permission, pk=pk)
    next_url = request.GET.get('next', reverse('access_control:admin_permission_detail', args=[pk]))
    
    permission.is_active = not permission.is_active
    permission.save()
    
    status = _('granted') if permission.is_active else _('revoked')
    messages.success(request, _(f'Permission {status} successfully.'))
    
    return HttpResponseRedirect(next_url) 