"""
Forms for Blood Collection module.
"""

from django import forms
from django.utils import timezone
import re
from .models import BloodCollectionBooking


class BloodCollectionBookingForm(forms.ModelForm):
    """
    Form to schedule blood sample collection with clinical validation.
    """
    TIME_SLOT_CHOICES = [
        ('07:30 AM - 08:30 AM (Fasting Preferred)', '07:30 AM - 08:30 AM (Fasting Preferred)'),
        ('08:30 AM - 09:30 AM (Fasting Preferred)', '08:30 AM - 09:30 AM (Fasting Preferred)'),
        ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
        ('11:30 AM - 12:30 PM', '11:30 AM - 12:30 PM'),
        ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
        ('03:30 PM - 04:30 PM', '03:30 PM - 04:30 PM'),
    ]

    time_slot = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_blood_time_slot'})
    )

    class Meta:
        model = BloodCollectionBooking
        fields = [
            'patient_name',
            'contact_number',
            'collection_date',
            'time_slot',
            'collection_location',
            'fasting_required',
            'special_notes',
        ]
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name of patient for laboratory requisition',
                'id': 'id_patient_name'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +1 (555) 234-5678',
                'id': 'id_contact_number'
            }),
            'collection_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_collection_date'
            }),
            'collection_location': forms.Select(
                choices=BloodCollectionBooking.LOCATION_CHOICES,
                attrs={'class': 'form-select', 'id': 'id_collection_location'}
            ),
            'fasting_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_fasting_required'
            }),
            'special_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special medical requests, mobility accommodations, or tests ordered by your physician...',
                'id': 'id_special_notes'
            }),
        }

    def clean_collection_date(self):
        collection_date = self.cleaned_data.get('collection_date')
        if collection_date and collection_date < timezone.now().date():
            raise forms.ValidationError("Collection date cannot be in the past. Please select today or a future date.")
        return collection_date

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number', '').strip()
        # Allow numbers, spaces, plus, hyphens, parentheses, at least 7 digits
        digits_only = re.sub(r'\D', '', contact_number)
        if len(digits_only) < 7:
            raise forms.ValidationError("Please provide a valid contact phone number with at least 7 digits.")
        return contact_number
