"""
Models for Doctor Consultation module in CRPify Patient Portal.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

UserModel = get_user_model()


class Doctor(models.Model):
    """
    Doctor directory model storing verified practitioner credentials.
    """
    MODE_CHOICES = [
        ('both', 'In-Person & Online'),
        ('in_person', 'In-Person Only'),
        ('online', 'Online Only'),
    ]

    name = models.CharField(max_length=150)
    qualifications = models.CharField(max_length=150, help_text="e.g. MD, FACP, Dip. Clinical Pathology")
    specialty = models.CharField(max_length=120, help_text="e.g. Internal Medicine & Inflammatory Disorders")
    consultation_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='both')
    experience_years = models.PositiveIntegerField(default=10)
    hospital_affiliation = models.CharField(max_length=200, blank=True, default="CRPify Partner Clinic")
    available_days = models.CharField(max_length=100, default="Mon - Fri")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"Dr. {self.name} — {self.specialty}"


class Consultation(models.Model):
    """
    Patient appointment booking for medical consultation.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    TYPE_CHOICES = [
        ('in_person', 'In-Person Clinic Visit'),
        ('online', 'Online Consultation'),
    ]

    patient = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=50)  # e.g., "09:00 AM - 09:30 AM"
    consultation_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='in_person')
    reason_for_consultation = models.TextField(blank=True, help_text="Optional reason or symptoms for the doctor")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date', '-created_at']

    def __str__(self):
        return f"Consultation with {self.doctor.name} on {self.appointment_date} ({self.status})"

    @property
    def can_cancel(self):
        """Allows cancellation of upcoming pending or confirmed appointments."""
        return self.status in ['pending', 'confirmed'] and self.appointment_date >= timezone.now().date()
