"""
Forms for Doctor Consultation module.
"""

from django import forms
from django.utils import timezone
from .models import Consultation, Doctor


class ConsultationBookingForm(forms.ModelForm):
    """
    Form to schedule a doctor consultation with strict server-side validation.
    """
    TIME_SLOT_CHOICES = [
        ('09:00 AM - 09:30 AM', '09:00 AM - 09:30 AM'),
        ('10:00 AM - 10:30 AM', '10:00 AM - 10:30 AM'),
        ('11:30 AM - 12:00 PM', '11:30 AM - 12:00 PM'),
        ('02:00 PM - 02:30 PM', '02:00 PM - 02:30 PM'),
        ('03:30 PM - 04:00 PM', '03:30 PM - 04:00 PM'),
        ('04:30 PM - 05:00 PM', '04:30 PM - 05:00 PM'),
    ]

    time_slot = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_time_slot'})
    )

    class Meta:
        model = Consultation
        fields = ['doctor', 'appointment_date', 'time_slot', 'consultation_type', 'reason_for_consultation']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'}),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_appointment_date'
            }),
            'consultation_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_consultation_type'}),
            'reason_for_consultation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Briefly describe the reason for your consultation, key symptoms, or clinical background (optional)...',
                'id': 'id_reason'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True)

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date and appointment_date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past. Please select today or a future date.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')
        consultation_type = cleaned_data.get('consultation_type')

        if doctor and appointment_date and time_slot:
            # Check for double booking
            clashing_appointment = Consultation.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                time_slot=time_slot,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if clashing_appointment:
                raise forms.ValidationError(
                    f"Dr. {doctor.name} already has an appointment scheduled on {appointment_date} at {time_slot}. Please select another time slot or date."
                )

            # Check if doctor supports the requested consultation mode
            if doctor.consultation_mode == 'in_person' and consultation_type == 'online':
                raise forms.ValidationError(f"Dr. {doctor.name} only provides in-person consultations.")
            elif doctor.consultation_mode == 'online' and consultation_type == 'in_person':
                raise forms.ValidationError(f"Dr. {doctor.name} is currently available for online consultations only.")

        return cleaned_data
