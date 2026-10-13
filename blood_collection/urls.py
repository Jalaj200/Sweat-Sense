"""
URL patterns for blood_collection app.
"""

from django.urls import path
from . import views

app_name = 'blood_collection'

urlpatterns = [
    path('', views.booking_list_view, name='list'),
    path('cancel/<int:pk>/', views.cancel_booking_view, name='cancel'),
]
