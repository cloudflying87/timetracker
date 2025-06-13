from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class PayRate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pay_rate')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ${self.hourly_rate}/hr"


class HourLimit(models.Model):
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, unique=True)
    max_hours = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_period_display()} limit: {self.max_hours} hours"


class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_entries')
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-clock_in']

    def __str__(self):
        return f"{self.user.username} - {self.clock_in.strftime('%Y-%m-%d %H:%M')}"

    @property
    def duration(self):
        if self.clock_out:
            return self.clock_out - self.clock_in
        return timezone.now() - self.clock_in

    @property
    def hours(self):
        duration = self.duration
        return duration.total_seconds() / 3600

    def save(self, *args, **kwargs):
        if self.clock_out and self.clock_out <= self.clock_in:
            raise ValueError("Clock out time must be after clock in time")
        super().save(*args, **kwargs)
