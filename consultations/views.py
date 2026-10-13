"""
Views for Doctor Consultation module.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import Doctor, Consultation
from .forms import ConsultationBookingForm


@login_required(login_url='accounts:login')
def consultation_list_view(request):
    """
    Renders the Doctor Consultation section (/consultation/).
    Displays verified doctor directory, upcoming bookings, past history, and booking form.
    """
    patient = request.user
    today = timezone.now().date()

    if request.method == 'POST':
        form = ConsultationBookingForm(data=request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.save()
            messages.success(
                request,
                f"Consultation with Dr. {consultation.doctor.name} on {consultation.appointment_date} ({consultation.time_slot}) has been successfully scheduled."
            )
            return redirect('consultations:list')
        else:
            messages.error(request, "Unable to schedule consultation. Please check the form errors below.")
    else:
        form = ConsultationBookingForm()

    doctors = Doctor.objects.filter(is_active=True)
    all_consultations = Consultation.objects.filter(patient=patient)

    upcoming_consultations = all_consultations.filter(
        appointment_date__gte=today
    ).exclude(status='cancelled')

    past_consultations = all_consultations.filter(
        appointment_date__lt=today
    ) | all_consultations.filter(status='cancelled')

    context = {
        'page_title': 'Doctor Consultation — Sweat Sense',
        'active_section': 'consultation',
        'doctors': doctors,
        'upcoming_consultations': upcoming_consultations,
        'past_consultations': past_consultations,
        'form': form,
    }
    return render(request, 'consultations/consultation_list.html', context)


@login_required(login_url='accounts:login')
@require_POST
def cancel_consultation_view(request, pk):
    """
    Allows a patient to cancel their own upcoming consultation.
    """
    consultation = get_object_or_404(Consultation, pk=pk, patient=request.user)

    if consultation.can_cancel:
        consultation.status = 'cancelled'
        consultation.save()
        messages.info(
            request,
            f"Your appointment with Dr. {consultation.doctor.name} on {consultation.appointment_date} has been cancelled."
        )
    else:
        messages.warning(request, "This appointment cannot be cancelled.")

    return redirect('consultations:list')
