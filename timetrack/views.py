from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from .forms import CustomUserCreationForm, TimeEntryForm, ClockInForm
from .models import TimeEntry, PayRate, HourLimit


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'timetrack/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    now = timezone.now()
    
    # Get current active time entry (if any)
    active_entry = TimeEntry.objects.filter(user=user, clock_out__isnull=True).first()
    
    # Calculate hours for current week
    week_start = now - timedelta(days=now.weekday())
    week_entries = TimeEntry.objects.filter(
        user=user,
        clock_in__gte=week_start
    ).exclude(clock_out__isnull=True)
    
    week_hours = sum([entry.hours for entry in week_entries])
    
    # Calculate hours for current month
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_entries = TimeEntry.objects.filter(
        user=user,
        clock_in__gte=month_start
    ).exclude(clock_out__isnull=True)
    
    month_hours = sum([entry.hours for entry in month_entries])
    
    # Get recent entries
    recent_entries = TimeEntry.objects.filter(user=user).order_by('-clock_in')[:10]
    
    context = {
        'active_entry': active_entry,
        'week_hours': week_hours,
        'month_hours': month_hours,
        'recent_entries': recent_entries,
    }
    
    return render(request, 'timetrack/dashboard.html', context)


@login_required
def clock_in(request):
    # Check if user already has an active time entry
    active_entry = TimeEntry.objects.filter(user=request.user, clock_out__isnull=True).first()
    
    if active_entry:
        messages.warning(request, 'You already have an active time entry. Please clock out first.')
        return redirect('dashboard')
    
    # Create time entry immediately without form
    time_entry = TimeEntry.objects.create(
        user=request.user,
        clock_in=timezone.now(),
        description=''
    )
    messages.success(request, 'Clocked in successfully!')
    return redirect('dashboard')


@login_required
def clock_out(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user, clock_out__isnull=True)
    
    # Clock out immediately without confirmation
    entry.clock_out = timezone.now()
    entry.save()
    messages.success(request, f'Clocked out successfully! Total time: {entry.hours:.2f} hours')
    return redirect('dashboard')


@login_required
def time_entry_create(request):
    if request.method == 'POST':
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            time_entry = form.save(commit=False)
            time_entry.user = request.user
            time_entry.save()
            messages.success(request, 'Time entry created successfully!')
            return redirect('dashboard')
    else:
        form = TimeEntryForm()
    
    return render(request, 'timetrack/time_entry_form.html', {'form': form})


@login_required
def time_entry_edit(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        form = TimeEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Time entry updated successfully!')
            return redirect('dashboard')
    else:
        form = TimeEntryForm(instance=entry)
    
    return render(request, 'timetrack/time_entry_form.html', {'form': form, 'entry': entry})


@login_required
def time_entry_delete(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Time entry deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'timetrack/time_entry_confirm_delete.html', {'entry': entry})
