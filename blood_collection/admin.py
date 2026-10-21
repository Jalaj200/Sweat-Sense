from django.contrib import admin
from .models import BloodCollectionBooking, ServiceablePincode


@admin.register(BloodCollectionBooking)
class BloodCollectionBookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient',
        'patient_name',
        'collection_method',
        'collection_date',
        'time_slot',
        'pin_code',
        'status',
        'created_at'
    )
    list_filter = ('collection_method', 'status', 'collection_date', 'fasting_required')
    search_fields = (
        'patient__username',
        'patient_name',
        'contact_number',
        'contact_phone',
        'pin_code',
        'area',
        'city',
        'collection_location'
    )
    readonly_fields = ('created_at',)


@admin.register(ServiceablePincode)
class ServiceablePincodeAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'area_name', 'city', 'state', 'is_active', 'max_slots_per_day', 'created_at')
    list_filter = ('is_active', 'city', 'state')
    search_fields = ('pincode', 'area_name', 'city', 'state')
