# Create your models here.
from django.conf import settings
from django.db import models
import uuid
from shopManagement.models import ShopProfile, ShopService

#Create a booking
class Booking(models.Model):
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.CharField(blank=True, null=True,max_length=250)
    status = models.CharField(blank=True, null=True,max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shop_profile = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, null = True)
    booking_date = models.DateField(null=True)
    booking_time = models.TimeField(null=True)
    shop_service = models.ForeignKey(ShopService, on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  

    def __str__(self) -> str:
        return self.user_name or "(No Name)"

class BookingService(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    shop_service = models.ForeignKey(ShopService, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Booking {self.booking.booking_id} - Service {self.shop_service.name}"

#Store Frequency of bookings made per shop 
class ShopBookingsCounter(models.Model):
    num_of_bookings = models.IntegerField(default=0, help_text="number of bookings for that barber in that date and time")
    shop_profile = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, null = True)
    booking_date = models.DateField(null=True)
    booking_time = models.TimeField(null=True)

