from django.urls import path

from .views import (barber_available_slots,create_booking, get_upcoming_bookings, update_booking_status)

urlpatterns = [
    path("shop/<uuid:shop_id>/slots",barber_available_slots,name="user_booking"),
    path("shop/<uuid:shop_id>/create",create_booking,name="create_booking"),
    path("shop/<uuid:shop_id>/get_bookings", get_upcoming_bookings, name = "get upcoming bookings for Shop"),
    path("update_booking_status", update_booking_status, name = "Update Booking Status")
]
