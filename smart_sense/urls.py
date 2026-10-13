"""
URL Configuration for Sweat Sense Patient Healthcare Portal.
Implements the exact five primary healthcare portal sections:
1. /dashboard/        -> Home
2. /consultation/     -> Doctor Consultation
3. /blood-collection/ -> Blood Collection
4. /reports/          -> Reports
5. /history/          -> History
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from accounts import views as account_views
from dashboard import views as dashboard_views
from consultations import views as consultation_views
from blood_collection import views as blood_views
from reports import views as report_views


def root_portal_redirect(request):
    """Directs authenticated patients to dashboard and guests to login."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('accounts:login')


urlpatterns = [
    path('admin/', admin.site.urls),

    # Root entry point
    path('', root_portal_redirect, name='root'),

    # Exact Five Primary Navigation Routes
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('consultation/', include('consultations.urls', namespace='consultations')),
    path('blood-collection/', include('blood_collection.urls', namespace='blood_collection')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('history/', dashboard_views.history_view, name='history'),

    # Direct top-level name shortcuts
    path('dashboard/', dashboard_views.home_view, name='dashboard_direct'),
    path('consultation/', consultation_views.consultation_list_view, name='consultation_direct'),
    path('blood-collection/', blood_views.booking_list_view, name='blood_collection_direct'),
    path('reports/', report_views.report_list_view, name='reports_direct'),

    # Authentication Routes
    path('', include('accounts.urls', namespace='accounts')),
    path('login/', account_views.login_view, name='login'),
    path('signup/', account_views.signup_view, name='signup'),
    path('logout/', account_views.logout_view, name='logout'),
]
