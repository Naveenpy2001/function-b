from django.urls import path
from .views import (
    BookingListCreateAPIView,
    BookingRetrieveUpdateAPIView,
    BookingDatesAPIView,
    PendingBookingsAPIView,
    ConfirmBookingAPIView,
    RejectBookingAPIView,
    ContactView
)

urlpatterns = [
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingRetrieveUpdateAPIView.as_view(), name='booking-detail'),
    path('bookings/dates/', BookingDatesAPIView.as_view(), name='booking-dates'),
    path('bookings/pending/', PendingBookingsAPIView.as_view(), name='pending-bookings'),
    path('bookings/<int:pk>/confirm/', ConfirmBookingAPIView.as_view(), name='confirm-booking'),
    path('bookings/<int:pk>/reject/', RejectBookingAPIView.as_view(), name='reject-booking'),
    path('contact/', ContactView.as_view(), name='reject-booking'),
]