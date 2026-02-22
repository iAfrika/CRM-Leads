from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Count, Case, When, Value, F, ExpressionWrapper, fields, Avg, Q
from django.utils import timezone
from ..models import Project, ProjectMilestone

@login_required
@permission_required('project_management.view_project_dashboard', raise_exception=True)
def project_dashboard(request):
    # Get overall project statistics
    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='in_progress').count()
    completed_projects = Project.objects.filter(status='completed').count()
    overdue_projects = Project.objects.filter(
        end_date__lt=timezone.now().date(),
        status__in=['planning', 'in_progress']
    ).count()

    # Get projects by status
    status_stats = Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Get projects by priority
    priority_stats = Project.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    # Get financial overview
    total_budget = Project.objects.aggregate(total=Sum('budget'))['total'] or 0
    total_actual_cost = Project.objects.aggregate(total=Sum('actual_cost'))['total'] or 0
    total_expenses = sum(project.get_total_expenses() for project in Project.objects.all())
    total_invoices = sum(project.get_total_invoices() for project in Project.objects.all())

    # Get recent projects
    recent_projects = Project.objects.order_by('-created_at')[:5]

    # Get upcoming milestones
    upcoming_milestones = ProjectMilestone.objects.filter(
        is_completed=False,
        due_date__gte=timezone.now().date()
    ).order_by('due_date')[:5]

    # Calculate project performance metrics
    total_profit = total_invoices - total_expenses
    profit_margin = (total_profit / total_invoices * 100) if total_invoices > 0 else 0
    budget_utilization = (total_actual_cost / total_budget * 100) if total_budget > 0 else 0
    completion_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0

    context = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'overdue_projects': overdue_projects,
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'total_budget': total_budget,
        'total_actual_cost': total_actual_cost,
        'total_expenses': total_expenses,
        'total_invoices': total_invoices,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'budget_utilization': budget_utilization,
        'completion_rate': completion_rate,
        'recent_projects': recent_projects,
        'upcoming_milestones': upcoming_milestones,
        'title': 'Project Dashboard'
    }
    return render(request, 'project_management/project_dashboard.html', context)

@login_required
@permission_required('project_management.view_project_analytics', raise_exception=True)
def project_analytics(request):
    from django.db.models import F, ExpressionWrapper, fields, Avg, Q
    from django.utils import timezone
    import datetime

    # Get project completion trends with duration analysis
    completion_trend = Project.objects.filter(
        status='completed'
    ).annotate(
        duration=ExpressionWrapper(
            F('end_date') - F('start_date'),
            output_field=fields.DurationField()
        )
    ).values('end_date__month').annotate(
        count=Count('id'),
        avg_duration=Avg('duration')
    ).order_by('end_date__month')

    # Get budget vs actual cost comparison with variance analysis
    budget_vs_actual = Project.objects.values('name').annotate(
        budget=Sum('budget'),
        actual=Sum('actual_cost'),
        variance=ExpressionWrapper(
            F('budget') - F('actual_cost'),
            output_field=fields.FloatField()
        ),
        variance_percentage=ExpressionWrapper(
            (F('budget') - F('actual_cost')) * 100.0 / F('budget'),
            output_field=fields.FloatField()
        )
    ).filter(budget__isnull=False, actual_cost__isnull=False)

    # Get milestone completion analysis
    milestone_analysis = ProjectMilestone.objects.values('project__name').annotate(
        total_milestones=Count('id'),
        completed_milestones=Count('id', filter=Q(is_completed=True)),
        completion_rate=ExpressionWrapper(
            Count('id', filter=Q(is_completed=True)) * 100.0 / Count('id'),
            output_field=fields.FloatField()
        ),
        overdue_milestones=Count('id', filter=Q(
            is_completed=False,
            due_date__lt=timezone.now().date()
        ))
    )

    # Get resource utilization metrics
    resource_utilization = Project.objects.filter(
        status='in_progress'
    ).values(
        'team_members__first_name',
        'team_members__last_name'
    ).annotate(
        assigned_projects=Count('id'),
        total_budget_managed=Sum('budget'),
        active_milestones=Count('milestones', filter=Q(
            milestones__is_completed=False,
            milestones__due_date__gte=timezone.now().date()
        ))
    ).order_by('-assigned_projects')

    # Get project health metrics
    project_health = Project.objects.filter(
        status='in_progress'
    ).annotate(
        budget_health=Case(
            When(actual_cost__gt=F('budget'), then=Value('over_budget')),
            When(actual_cost__lte=0.8 * F('budget'), then=Value('under_budget')),
            default=Value('on_track'),
            output_field=fields.CharField(),
        ),
        schedule_health=Case(
            When(end_date__lt=timezone.now().date(), then=Value('delayed')),
            When(end_date__gt=timezone.now().date() + datetime.timedelta(days=30), then=Value('on_track')),
            default=Value('at_risk'),
            output_field=fields.CharField(),
        )
    ).values('budget_health', 'schedule_health').annotate(
        count=Count('id')
    )

    # Get project status and priority distributions
    status_distribution = Project.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    priority_distribution = Project.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    # Get client project distribution
    client_distribution = Project.objects.values('client__name').annotate(
        count=Count('id'),
        total_budget=Sum('budget'),
        total_revenue=Sum('actual_cost')
    ).order_by('-count')[:10]

    context = {
        'completion_trend': completion_trend,
        'budget_vs_actual': budget_vs_actual,
        'status_distribution': status_distribution,
        'priority_distribution': priority_distribution,
        'client_distribution': client_distribution,
        'resource_utilization': resource_utilization,
        'milestone_analysis': milestone_analysis,
        'project_health': project_health,
        'title': 'Project Analytics'
    }
    return render(request, 'project_management/project_analytics.html', context)