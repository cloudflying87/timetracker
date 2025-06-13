from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, F, Q
from datetime import datetime, timedelta
from .models import TimeEntry, PayRate, HourLimit


@staff_member_required
def admin_dashboard(request):
    now = timezone.now()
    
    # Get hour limits
    weekly_limit = HourLimit.objects.filter(period='weekly').first()
    monthly_limit = HourLimit.objects.filter(period='monthly').first()
    
    # Calculate current week and month usage
    week_start = now - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get all completed time entries for the current period
    week_entries = TimeEntry.objects.filter(
        clock_in__gte=week_start,
        clock_out__isnull=False
    )
    
    month_entries = TimeEntry.objects.filter(
        clock_in__gte=month_start,
        clock_out__isnull=False
    )
    
    # Calculate total hours
    week_total_hours = sum([entry.hours for entry in week_entries])
    month_total_hours = sum([entry.hours for entry in month_entries])
    
    # Calculate usage percentages
    week_usage_percent = 0
    if weekly_limit and weekly_limit.max_hours > 0:
        week_usage_percent = (week_total_hours / float(weekly_limit.max_hours)) * 100
    
    month_usage_percent = 0
    if monthly_limit and monthly_limit.max_hours > 0:
        month_usage_percent = (month_total_hours / float(monthly_limit.max_hours)) * 100
    
    # Get user statistics with pay calculations
    users_stats = []
    for user in User.objects.filter(is_active=True, is_staff=False):
        user_week_entries = week_entries.filter(user=user)
        user_month_entries = month_entries.filter(user=user)
        
        user_week_hours = sum([entry.hours for entry in user_week_entries])
        user_month_hours = sum([entry.hours for entry in user_month_entries])
        
        # Get pay rate
        pay_rate = PayRate.objects.filter(user=user).first()
        hourly_rate = pay_rate.hourly_rate if pay_rate else 0
        
        users_stats.append({
            'user': user,
            'week_hours': user_week_hours,
            'month_hours': user_month_hours,
            'hourly_rate': hourly_rate,
            'week_pay': user_week_hours * float(hourly_rate),
            'month_pay': user_month_hours * float(hourly_rate),
        })
    
    # Calculate total pay
    total_week_pay = sum([stat['week_pay'] for stat in users_stats])
    total_month_pay = sum([stat['month_pay'] for stat in users_stats])
    
    # Get recent time entries
    recent_entries = TimeEntry.objects.filter(clock_out__isnull=False).order_by('-clock_in')[:20]
    
    # Get currently clocked in users
    active_entries = TimeEntry.objects.filter(clock_out__isnull=True).select_related('user')
    
    context = {
        'weekly_limit': weekly_limit,
        'monthly_limit': monthly_limit,
        'week_total_hours': week_total_hours,
        'month_total_hours': month_total_hours,
        'week_usage_percent': week_usage_percent,
        'month_usage_percent': month_usage_percent,
        'users_stats': users_stats,
        'total_week_pay': total_week_pay,
        'total_month_pay': total_month_pay,
        'recent_entries': recent_entries,
        'active_entries': active_entries,
    }
    
    return render(request, 'timetrack/admin_dashboard.html', context)


@staff_member_required
def pay_report(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        # Default to current month
        now = timezone.now()
        start_date = now.replace(day=1).date()
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1).date() - timedelta(days=1)
        else:
            end_date = now.replace(month=now.month + 1, day=1).date() - timedelta(days=1)
    
    # Get time entries in date range
    entries = TimeEntry.objects.filter(
        clock_in__date__gte=start_date,
        clock_in__date__lte=end_date,
        clock_out__isnull=False
    ).select_related('user')
    
    # Group by user and calculate pay
    user_reports = {}
    for entry in entries:
        user = entry.user
        if user not in user_reports:
            pay_rate = PayRate.objects.filter(user=user).first()
            hourly_rate = pay_rate.hourly_rate if pay_rate else 0
            user_reports[user] = {
                'user': user,
                'entries': [],
                'total_hours': 0,
                'hourly_rate': hourly_rate,
                'total_pay': 0,
            }
        
        # Add pay calculation to each entry
        entry.pay = entry.hours * float(user_reports[user]['hourly_rate'])
        user_reports[user]['entries'].append(entry)
        user_reports[user]['total_hours'] += entry.hours
        user_reports[user]['total_pay'] += entry.pay
    
    # Calculate totals
    total_hours = sum([report['total_hours'] for report in user_reports.values()])
    total_pay = sum([report['total_pay'] for report in user_reports.values()])
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'user_reports': user_reports.values(),
        'total_hours': total_hours,
        'total_pay': total_pay,
    }
    
    return render(request, 'timetrack/pay_report.html', context)