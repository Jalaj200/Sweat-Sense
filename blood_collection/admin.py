from django.contrib import admin
from .models import BloodCollectionBooking


@admin.register(BloodCollectionBooking)
class BloodCollectionBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'patient_name', 'contact_number', 'collection_date', 'time_slot', 'status')
    list_filter = ('status', 'collection_date', 'fasting_required')
    search_fields = ('patient__username', 'patient_name', 'contact_number', 'collection_location')
