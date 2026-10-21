"""
Forms for Blood Collection module in CRPify Patient Portal.
Implements robust validation for both Home Blood Collection and Diagnostic Center bookings.
"""

from django import forms
from django.utils import timezone
import re
from .models import BloodCollectionBooking, check_pincode_serviceability


class BloodCollectionBookingForm(forms.ModelForm):
    """
    Form to schedule blood sample collection with clinical validation.
    Dynamically validates Home Blood Collection address requirements or Diagnostic Center selection.
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

    collection_method = forms.ChoiceField(
        choices=BloodCollectionBooking.METHOD_CHOICES,
        initial=BloodCollectionBooking.METHOD_HOME,
        widget=forms.RadioSelect(attrs={'class': 'btn-check', 'id': 'id_collection_method'}),
        required=False
    )

    class Meta:
        model = BloodCollectionBooking
        fields = [
            'collection_method',
            'patient_name',
            'contact_number',
            'collection_date',
            'time_slot',
            # Diagnostic Center
            'collection_location',
            # Home Collection Address Fields
            'house_number',
            'street',
            'area',
            'city',
            'state',
            'pin_code',
            'contact_person',
            'contact_phone',
            'landmark',
            'additional_directions',
            # Protocols
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
                'placeholder': 'e.g. +91 98765 43210 or (555) 234-5678',
                'id': 'id_contact_number'
            }),
            'collection_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_collection_date'
            }),
            'collection_location': forms.Select(
                choices=BloodCollectionBooking.CENTER_CHOICES,
                attrs={'class': 'form-select', 'id': 'id_collection_location'}
            ),
            'house_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Flat 402, Lotus Heights / House # 12-B',
                'id': 'id_house_number'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 10th Main Road, 4th Cross',
                'id': 'id_street'
            }),
            'area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Indiranagar, Connaught Place, Bandra West',
                'id': 'id_area'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. New Delhi, Mumbai, Bengaluru',
                'id': 'id_city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Delhi, Maharashtra, Karnataka',
                'id': 'id_state'
            }),
            'pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '6-digit PIN code (e.g. 110001, 560001)',
                'id': 'id_pin_code',
                'maxlength': '6',
                'pattern': '[0-9]{6}',
                'autocomplete': 'postal-code'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name of person available at address',
                'id': 'id_contact_person'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact phone for dispatch phlebotomist',
                'id': 'id_contact_phone'
            }),
            'landmark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prominent nearby landmark, metro station, or hospital (optional)',
                'id': 'id_landmark'
            }),
            'additional_directions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Gate number, floor level, bell instructions, or entry security notes (optional)...',
                'id': 'id_additional_directions'
            }),
            'fasting_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_fasting_required'
            }),
            'special_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Special medical requests, mobility accommodations, or tests ordered by your physician...',
                'id': 'id_special_notes'
            }),
        }

    def __init__(self, *args, patient=None, **kwargs):
        self.patient = patient
        super().__init__(*args, **kwargs)
        # By default make non-universal fields non-required at field level;
        # clean() handles conditional requirements depending on collection_method.
        self.fields['collection_location'].required = False
        self.fields['house_number'].required = False
        self.fields['street'].required = False
        self.fields['area'].required = False
        self.fields['city'].required = False
        self.fields['state'].required = False
        self.fields['pin_code'].required = False
        self.fields['contact_person'].required = False
        self.fields['contact_phone'].required = False

    def clean_collection_method(self):
        method = self.cleaned_data.get('collection_method')
        if not method:
            location = self.data.get('collection_location')
            if location in dict(BloodCollectionBooking.CENTER_CHOICES):
                return BloodCollectionBooking.METHOD_CENTER
            return BloodCollectionBooking.METHOD_HOME
        return method

    def clean_collection_date(self):
        collection_date = self.cleaned_data.get('collection_date')
        if collection_date and collection_date < timezone.now().date():
            raise forms.ValidationError("Collection date cannot be in the past. Please select today or a future date.")
        return collection_date

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number', '').strip()
        digits_only = re.sub(r'\D', '', contact_number)
        if len(digits_only) < 7:
            raise forms.ValidationError("Please provide a valid contact phone number with at least 7 digits.")
        return contact_number

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('collection_method')
        collection_date = cleaned_data.get('collection_date')
        time_slot = cleaned_data.get('time_slot')

        if method == BloodCollectionBooking.METHOD_HOME:
            # Validate required address fields
            house_number = cleaned_data.get('house_number', '').strip()
            street = cleaned_data.get('street', '').strip()
            area = cleaned_data.get('area', '').strip()
            city = cleaned_data.get('city', '').strip()
            state = cleaned_data.get('state', '').strip()
            pin_code = cleaned_data.get('pin_code', '').strip()
            contact_person = cleaned_data.get('contact_person', '').strip()
            contact_phone = cleaned_data.get('contact_phone', '').strip()

            if not house_number:
                self.add_error('house_number', "House / Flat / Building number is required for home collection.")
            if not street:
                self.add_error('street', "Street or Road address is required.")
            if not area:
                self.add_error('area', "Area or Locality is required.")
            if not city:
                self.add_error('city', "City is required.")
            if not state:
                self.add_error('state', "State is required.")

            # Validate PIN code and check serviceability
            if not pin_code:
                self.add_error('pin_code', "Six-digit postal PIN code is required.")
            else:
                is_serviceable, reason, info = check_pincode_serviceability(pin_code)
                if not is_serviceable:
                    self.add_error('pin_code', reason)
                else:
                    cleaned_data['pin_code'] = re.sub(r'\s+', '', pin_code)

            if not contact_person:
                self.add_error('contact_person', "Contact person name at collection address is required.")
            if not contact_phone:
                self.add_error('contact_phone', "Contact phone number for phlebotomist arrival is required.")
            else:
                digits_phone = re.sub(r'\D', '', contact_phone)
                if len(digits_phone) < 7:
                    self.add_error('contact_phone', "Please provide a valid contact phone number with at least 7 digits.")

            # Automatically set collection_location for home collections
            cleaned_data['collection_location'] = 'home_collection'

        elif method == BloodCollectionBooking.METHOD_CENTER:
            location = cleaned_data.get('collection_location', '').strip()
            valid_center_keys = [k for k, _ in BloodCollectionBooking.CENTER_CHOICES]
            if not location or location not in valid_center_keys:
                self.add_error('collection_location', "Please select a certified diagnostic center from the list.")

        # Check for slot collisions for the same patient
        if self.patient and collection_date and time_slot:
            existing_booking = BloodCollectionBooking.objects.filter(
                patient=self.patient,
                collection_date=collection_date,
                time_slot=time_slot
            ).exclude(status='cancelled')

            if self.instance and self.instance.pk:
                existing_booking = existing_booking.exclude(pk=self.instance.pk)

            if existing_booking.exists():
                raise forms.ValidationError(
                    "You already have a blood sample collection booking scheduled for this date and time slot."
                )

        return cleaned_data
