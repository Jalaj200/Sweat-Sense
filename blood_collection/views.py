"""
Views for Blood Collection module in CRPify Patient Portal.
Handles both Home Blood Sample Collection bookings and Diagnostic Center bookings.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import (
    BloodCollectionBooking,
    ServiceablePincode,
    check_pincode_serviceability,
    DEFAULT_SERVICEABLE_PINCODES
)
from .forms import BloodCollectionBookingForm


@login_required(login_url='accounts:login')
def booking_list_view(request):
    """
    Renders the Blood Collection section (/blood-collection/).
    Displays booking scheduling form with dynamic Home Collection address or Center selection,
    upcoming active requisitions, and past collections history.
    """
    patient = request.user
    today = timezone.now().date()
    default_name = patient.get_full_name() or patient.username

    if request.method == 'POST':
        form = BloodCollectionBookingForm(data=request.POST, patient=patient)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.patient = patient
            booking.save()

            if booking.collection_method == BloodCollectionBooking.METHOD_HOME:
                messages.success(
                    request,
                    f"Home blood collection booked successfully for {booking.patient_name} on "
                    f"{booking.collection_date} ({booking.time_slot}). Our dispatch desk has registered "
                    f"your address at {booking.area}, {booking.city} ({booking.pin_code})."
                )
            else:
                messages.success(
                    request,
                    f"Blood collection booked successfully for {booking.patient_name} at "
                    f"{booking.get_collection_location_display()} on {booking.collection_date} ({booking.time_slot})."
                )
            return redirect('blood_collection:list')
        else:
            messages.error(
                request,
                "Unable to schedule blood collection. Please review the highlighted errors below."
            )
    else:
        # Pre-fill patient's details
        form = BloodCollectionBookingForm(
            patient=patient,
            initial={
                'patient_name': default_name,
                'contact_person': default_name,
                'collection_method': BloodCollectionBooking.METHOD_HOME,
                'city': 'New Delhi',
                'state': 'Delhi',
            }
        )

    all_bookings = BloodCollectionBooking.objects.filter(patient=patient)

    upcoming_bookings = all_bookings.filter(
        collection_date__gte=today
    ).exclude(status='cancelled')

    past_bookings = all_bookings.filter(
        collection_date__lt=today
    ) | all_bookings.filter(status='cancelled')

    # Configured serviceable PIN count
    serviceable_count = ServiceablePincode.objects.filter(is_active=True).count()
    if serviceable_count == 0:
        serviceable_count = len(DEFAULT_SERVICEABLE_PINCODES)

    context = {
        'page_title': 'Blood Collection Services — CRPify',
        'active_section': 'blood_collection',
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'form': form,
        'serviceable_count': serviceable_count,
        'default_serviceable_pincodes': DEFAULT_SERVICEABLE_PINCODES[:8],  # Sample for user guidance
    }
    return render(request, 'blood_collection/booking_list.html', context)


@login_required(login_url='accounts:login')
def check_pincode_api_view(request):
    """
    JSON API for real-time frontend PIN code serviceability validation.
    GET /blood-collection/api/check-pincode/?pincode=110001
    """
    pincode = request.GET.get('pincode', '').strip()
    is_serviceable, message, details = check_pincode_serviceability(pincode)
    return JsonResponse({
        'pincode': pincode,
        'serviceable': is_serviceable,
        'message': message,
        'details': details or {},
    })


@login_required(login_url='accounts:login')
@require_POST
def cancel_booking_view(request, pk):
    """
    Allows a patient to cancel an upcoming blood collection booking.
    """
    booking = get_object_or_404(BloodCollectionBooking, pk=pk, patient=request.user)

    if booking.can_cancel:
        booking.status = 'cancelled'
        booking.save()
        messages.info(
            request,
            f"Your blood collection scheduled for {booking.collection_date} has been cancelled."
        )
    else:
        messages.warning(request, "This collection booking cannot be cancelled.")

    return redirect('blood_collection:list')
