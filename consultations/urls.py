"""
URL patterns for consultations app.
"""

from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('', views.consultation_list_view, name='list'),
    path('cancel/<int:pk>/', views.cancel_consultation_view, name='cancel'),
]
