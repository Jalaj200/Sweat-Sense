from django.contrib import admin
from .models import Doctor, Consultation


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'qualifications', 'specialty', 'consultation_mode', 'is_active')
    list_filter = ('specialty', 'consultation_mode', 'is_active')
    search_fields = ('name', 'specialty', 'qualifications')


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'appointment_date', 'time_slot', 'consultation_type', 'status')
    list_filter = ('status', 'consultation_type', 'appointment_date')
    search_fields = ('patient__username', 'patient__email', 'doctor__name', 'reason_for_consultation')
