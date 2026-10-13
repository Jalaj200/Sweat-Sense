"""
URL patterns for reports app.
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list_view, name='list'),
    path('view/<int:pk>/', views.secure_view_report_view, name='view'),
    path('download/<int:pk>/', views.secure_download_report_view, name='download'),
]
