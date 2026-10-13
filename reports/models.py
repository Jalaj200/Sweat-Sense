"""
Models for Medical Reports module in Sweat Sense Patient Portal.
"""

from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class MedicalReport(models.Model):
    """
    Validated clinical laboratory reports associated with authenticated patients.
    PDF files are stored securely and delivered via authenticated streaming.
    """
    CATEGORY_CHOICES = [
        ('inflammation', 'Inflammatory Biomarkers (Serum CRP)'),
        ('biochemistry', 'Clinical Biochemistry & Metabolic Panel'),
        ('hematology', 'Complete Blood Count (CBC)'),
        ('general', 'General Diagnostic Pathology Report'),
    ]

    STATUS_CHOICES = [
        ('ready', 'Final Validated Report'),
        ('preliminary', 'Preliminary Finding'),
    ]

    patient = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='biochemistry')
    issuing_lab = models.CharField(max_length=200, default="Sweat Sense Partner Reference Laboratory")
    report_date = models.DateField()
    pdf_file = models.FileField(upload_to='secure_reports/%Y/%m/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')
    notes = models.TextField(blank=True, help_text="Notes from clinical pathologist or laboratory director")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date', '-uploaded_at']

    def __str__(self):
        return f"{self.title} — {self.patient.username} ({self.report_date})"
