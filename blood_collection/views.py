"""
Views for Blood Collection module.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import BloodCollectionBooking
from .forms import BloodCollectionBookingForm


@login_required(login_url='accounts:login')
def booking_list_view(request):
    """
    Renders the Blood Collection section (/blood-collection/).
    Displays booking scheduling form, upcoming appointments, and past collections.
    """
    patient = request.user
    today = timezone.now().date()

    if request.method == 'POST':
        form = BloodCollectionBookingForm(data=request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.patient = patient
            booking.save()
            messages.success(
                request,
                f"Blood collection booked successfully for {booking.patient_name} on {booking.collection_date} ({booking.time_slot})."
            )
            return redirect('blood_collection:list')
        else:
            messages.error(request, "Unable to schedule blood collection. Please review the highlighted issues.")
    else:
        # Pre-fill patient's full name if available
        default_name = patient.get_full_name() or patient.username
        form = BloodCollectionBookingForm(initial={'patient_name': default_name})

    all_bookings = BloodCollectionBooking.objects.filter(patient=patient)

    upcoming_bookings = all_bookings.filter(
        collection_date__gte=today
    ).exclude(status='cancelled')

    past_bookings = all_bookings.filter(
        collection_date__lt=today
    ) | all_bookings.filter(status='cancelled')

    context = {
        'page_title': 'Blood Collection — Sweat Sense',
        'active_section': 'blood_collection',
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'form': form,
    }
    return render(request, 'blood_collection/booking_list.html', context)


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
