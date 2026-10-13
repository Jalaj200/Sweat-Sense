"""
Models for Blood Collection module in Sweat Sense Patient Portal.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

UserModel = get_user_model()


class BloodCollectionBooking(models.Model):
    """
    Blood sample collection booking for laboratory pathology analysis.
    Distinguished from sweat-based CRP biosensing research.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed Scheduled'),
        ('completed', 'Sample Collected'),
        ('cancelled', 'Cancelled'),
    ]

    LOCATION_CHOICES = [
        ('lab_central', 'Sweat Sense Diagnostic Center — Central Lab (Suite 201)'),
        ('lab_north', 'Sweat Sense Diagnostic Center — North Pathology Wing'),
        ('home_collection', 'Home Phlebotomy Collection (Verified Address)'),
    ]

    patient = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='blood_bookings')
    patient_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=30)
    collection_date = models.DateField()
    time_slot = models.CharField(max_length=50)  # e.g., "07:30 AM - 08:30 AM (Fasting Preferred)"
    collection_location = models.CharField(max_length=255, choices=LOCATION_CHOICES, default='lab_central')
    fasting_required = models.BooleanField(
        default=True,
        help_text="Standard 8-10 hour fasting recommended for metabolic and lipid accuracy."
    )
    special_notes = models.TextField(blank=True, help_text="Optional notes, accessibility needs, or prescription refs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-collection_date', '-created_at']

    def __str__(self):
        return f"Blood Collection for {self.patient_name} on {self.collection_date} ({self.status})"

    @property
    def can_cancel(self):
        """Allows cancellation of upcoming pending or confirmed collections."""
        return self.status in ['pending', 'confirmed'] and self.collection_date >= timezone.now().date()
