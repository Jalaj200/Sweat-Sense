"""
Views for dashboard and history modules in CRPify Patient Portal.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from consultations.models import Consultation
from blood_collection.models import BloodCollectionBooking
from reports.models import MedicalReport


@login_required(login_url='accounts:login')
def home_view(request):
    """
    Renders Section 1: Home Dashboard (/dashboard/).
    Displays patient overview, quick action cards, CRP educational card,
    upcoming appointments, upcoming blood collections, and recent reports.
    """
    patient = request.user
    today = timezone.now().date()
    display_name = patient.get_full_name() or patient.username

    # Upcoming patient consultations
    upcoming_consultations = Consultation.objects.filter(
        patient=patient,
        appointment_date__gte=today
    ).exclude(status='cancelled').select_related('doctor')[:3]

    # Upcoming blood collection bookings
    upcoming_blood_bookings = BloodCollectionBooking.objects.filter(
        patient=patient,
        collection_date__gte=today
    ).exclude(status='cancelled')[:3]

    # Recent medical reports
    recent_reports = MedicalReport.objects.filter(
        patient=patient
    )[:3]

    # Summary metrics
    consultation_count = Consultation.objects.filter(patient=patient).count()
    blood_booking_count = BloodCollectionBooking.objects.filter(patient=patient).count()
    report_count = MedicalReport.objects.filter(patient=patient).count()

    context = {
        'page_title': 'Patient Portal Home — CRPify',
        'active_section': 'home',
        'display_name': display_name,
        'user': patient,
        'upcoming_consultations': upcoming_consultations,
        'upcoming_blood_bookings': upcoming_blood_bookings,
        'recent_reports': recent_reports,
        'consultation_count': consultation_count,
        'blood_booking_count': blood_booking_count,
        'report_count': report_count,
    }
    return render(request, 'dashboard/home.html', context)


@login_required(login_url='accounts:login')
def history_view(request):
    """
    Renders Section 5: History (/history/).
    Displays chronological healthcare timeline with interactive category filtering.
    """
    patient = request.user
    category_filter = request.GET.get('filter', 'all').lower()

    # Fetch patient's actual records
    consultations_qs = Consultation.objects.filter(patient=patient).select_related('doctor')
    blood_qs = BloodCollectionBooking.objects.filter(patient=patient)
    reports_qs = MedicalReport.objects.filter(patient=patient)

    timeline_items = []

    # Map Consultations to timeline items
    if category_filter in ['all', 'consultation']:
        for c in consultations_qs:
            timeline_items.append({
                'category': 'consultation',
                'category_label': 'Doctor Consultation',
                'icon': 'bi-person-badge',
                'icon_bg': 'bg-primary-subtle text-primary',
                'title': f"Consultation with Dr. {c.doctor.name}",
                'subtitle': f"{c.doctor.specialty} • {c.get_consultation_type_display()}",
                'date': c.appointment_date,
                'created_at': c.created_at,
                'time_slot': c.time_slot,
                'status': c.get_status_display(),
                'status_raw': c.status,
                'record_id': f"CON-{c.id:04d}",
                'url': '/consultation/',
            })

    # Map Blood Collections to timeline items
    if category_filter in ['all', 'blood_collection']:
        for b in blood_qs:
            if getattr(b, 'collection_method', '') == 'HOME':
                method_label = "Home Blood Collection"
                icon_name = "bi-house-heart"
                subtitle_text = f"Home Phlebotomy: {b.full_address}"
            else:
                method_label = "Visit Diagnostic Center"
                icon_name = "bi-hospital"
                subtitle_text = f"Center: {b.get_collection_location_display()}"

            timeline_items.append({
                'category': 'blood_collection',
                'category_label': f"Blood Collection ({method_label})",
                'icon': icon_name,
                'icon_bg': 'bg-danger-subtle text-danger',
                'title': f"Phlebotomy Collection for {b.patient_name}",
                'subtitle': subtitle_text,
                'date': b.collection_date,
                'created_at': b.created_at,
                'time_slot': b.time_slot,
                'status': b.get_status_display(),
                'status_raw': b.status,
                'record_id': f"BLD-{b.id:04d}",
                'url': '/blood-collection/',
            })

    # Map Medical Reports to timeline items
    if category_filter in ['all', 'reports']:
        for r in reports_qs:
            timeline_items.append({
                'category': 'reports',
                'category_label': 'Medical Report',
                'icon': 'bi-file-earmark-medical',
                'icon_bg': 'bg-info-subtle text-info',
                'title': r.title,
                'subtitle': f"Issued by: {r.issuing_lab} • {r.get_category_display()}",
                'date': r.report_date,
                'created_at': r.uploaded_at,
                'time_slot': 'Laboratory Issued',
                'status': r.get_status_display(),
                'status_raw': r.status,
                'record_id': f"REP-{r.id:04d}",
                'url': f"/reports/view/{r.id}/",
            })

    # Sort chronological by date descending
    timeline_items.sort(key=lambda x: (x['date'], x['created_at']), reverse=True)

    context = {
        'page_title': 'Healthcare Activity History — CRPify',
        'active_section': 'history',
        'current_filter': category_filter,
        'timeline_items': timeline_items,
        'total_count': len(timeline_items),
        'consultations_count': consultations_qs.count(),
        'blood_count': blood_qs.count(),
        'reports_count': reports_qs.count(),
    }
    return render(request, 'history/history.html', context)
