from django.contrib import admin
from .models import TimeEntry, PayRate, HourLimit
from django.db.models import Sum, F
from datetime import datetime, timedelta
from django.utils import timezone


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'clock_in', 'clock_out', 'hours', 'description']
    list_filter = ['user', 'clock_in', 'clock_out']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'clock_in'
    ordering = ['-clock_in']

    def hours(self, obj):
        return f"{obj.hours:.2f}"
    hours.short_description = 'Hours'


@admin.register(PayRate)
class PayRateAdmin(admin.ModelAdmin):
    list_display = ['user', 'hourly_rate', 'updated_at']
    search_fields = ['user__username']


@admin.register(HourLimit)
class HourLimitAdmin(admin.ModelAdmin):
    list_display = ['period', 'max_hours', 'current_usage', 'percentage_used']
    
    def current_usage(self, obj):
        now = timezone.now()
        if obj.period == 'weekly':
            start_date = now - timedelta(days=now.weekday())
        else:  # monthly
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_hours = TimeEntry.objects.filter(
            clock_in__gte=start_date
        ).aggregate(
            total=Sum(F('clock_out') - F('clock_in'))
        )['total']
        
        if total_hours:
            hours = total_hours.total_seconds() / 3600
            return f"{hours:.2f}"
        return "0.00"
    current_usage.short_description = 'Current Hours'
    
    def percentage_used(self, obj):
        current = float(self.current_usage(obj))
        percentage = (current / float(obj.max_hours)) * 100
        return f"{percentage:.1f}%"
    percentage_used.short_description = '% Used'
