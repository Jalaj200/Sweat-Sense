from django.contrib import admin
from .models import MedicalReport


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'patient', 'category', 'report_date', 'status', 'issuing_lab')
    list_filter = ('category', 'status', 'report_date')
    search_fields = ('title', 'patient__username', 'patient__email', 'issuing_lab')
