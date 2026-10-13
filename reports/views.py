"""
Views for Medical Reports module.
Enforces strict patient-level access control on all report requests.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpResponse
from django.contrib import messages
from django.db.models import Q
from .models import MedicalReport


@login_required(login_url='accounts:login')
def report_list_view(request):
    """
    Renders the Reports section (/reports/).
    Displays filterable and searchable medical reports belonging strictly to the authenticated user.
    """
    patient = request.user
    reports_qs = MedicalReport.objects.filter(patient=patient)

    # Search query
    q = request.GET.get('q', '').strip()
    if q:
        reports_qs = reports_qs.filter(
            Q(title__icontains=q) |
            Q(issuing_lab__icontains=q) |
            Q(notes__icontains=q)
        )

    # Category filter
    category = request.GET.get('category', '').strip()
    if category and category != 'all':
        reports_qs = reports_qs.filter(category=category)

    # Date filter
    date_filter = request.GET.get('date', '').strip()
    if date_filter:
        reports_qs = reports_qs.filter(report_date=date_filter)

    categories = MedicalReport.CATEGORY_CHOICES

    context = {
        'page_title': 'Medical & Laboratory Reports — Sweat Sense',
        'active_section': 'reports',
        'reports': reports_qs,
        'categories': categories,
        'selected_category': category,
        'selected_date': date_filter,
        'search_query': q,
        'total_count': reports_qs.count(),
    }
    return render(request, 'reports/report_list.html', context)


@login_required(login_url='accounts:login')
def secure_view_report_view(request, pk):
    """
    Securely serves a medical report for viewing.
    Verifies that the authenticated user is the report's owner.
    """
    report = get_object_or_404(MedicalReport, pk=pk)

    # Enforce strict patient-level authorization
    if report.patient != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have authorization to view this medical report.")

    if report.pdf_file and report.pdf_file.storage.exists(report.pdf_file.name):
        return FileResponse(report.pdf_file.open('rb'), content_type='application/pdf')

    # If PDF is not uploaded yet, render a structured clinical summary page
    context = {
        'page_title': f'{report.title} — Sweat Sense',
        'report': report,
    }
    return render(request, 'reports/report_detail.html', context)


@login_required(login_url='accounts:login')
def secure_download_report_view(request, pk):
    """
    Securely downloads a medical report PDF with attachment header.
    Verifies that the authenticated user is the report's owner.
    """
    report = get_object_or_404(MedicalReport, pk=pk)

    # Enforce strict patient-level authorization
    if report.patient != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have authorization to download this medical report.")

    if report.pdf_file and report.pdf_file.storage.exists(report.pdf_file.name):
        filename = f"SweatSense_Report_{report.id}_{report.report_date}.pdf"
        return FileResponse(report.pdf_file.open('rb'), as_attachment=True, filename=filename)

    messages.info(
        request,
        f"The physical PDF document for '{report.title}' is being processed by the issuing laboratory."
    )
    return redirect('reports:view', pk=report.pk)
