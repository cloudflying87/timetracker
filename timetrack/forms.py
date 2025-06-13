from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TimeEntry
from django.utils import timezone


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['clock_in', 'clock_out', 'description']
        widgets = {
            'clock_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'clock_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        clock_in = cleaned_data.get('clock_in')
        clock_out = cleaned_data.get('clock_out')

        if clock_out and clock_in and clock_out <= clock_in:
            raise forms.ValidationError("Clock out time must be after clock in time.")

        return cleaned_data


class ClockInForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What are you working on? (optional)', 'required': False}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False