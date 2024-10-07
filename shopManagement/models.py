from django.db import models
import uuid

BOOKING_PERIOD = (
    ("5", "5M"),
    ("10", "10M"),
    ("15", "15M"),
    ("20", "20M"),
    ("25", "25M"),
    ("30", "30M"),
    ("35", "35M"),
    ("40", "40M"),
    ("45", "45M"),
    ("60", "1H"),
    ("75", "1H 15M"),
    ("90", "1H 30M"),
    ("105", "1H 45M"),
    ("120", "2H"),
    ("150", "2H 30M"),
    ("180", "3H"),
)

# Create your models here.
class ShopProfile(models.Model):
    shop_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shop_name = models.CharField(max_length=255)
    about_us = models.TextField()
    email = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=0.000000)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=0.000000)
    venue_amenities = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.shop_name

class ShopProfileImage(models.Model):
    image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shop_profile = models.ForeignKey(ShopProfile, related_name='images', on_delete=models.CASCADE)
    # TODO: change the upload_to to S3 url
    image = models.ImageField(upload_to='shop_images/')

class ShopService(models.Model):
    service_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shop_profile = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='service_name')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.DurationField(help_text="Duration of the service (e.g., 00:30:00 for 30 minutes)")
    
    def __str__(self):
        return f"{self.name} ({self.shop_profile.shop_name})"
    
class ShopServicesImage(models.Model):
    image_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    service = models.ForeignKey(ShopService, related_name='shop_service_images', on_delete=models.CASCADE)
    # TODO: change the upload_to to S3 url
    image = models.ImageField(upload_to='service_images/')
    description = models.CharField(max_length=255, null=True, blank=True)
    
class ShopSettings(models.Model):
    # General
    booking_enable = models.BooleanField(default=True)
    confirmation_required = models.BooleanField(default=True)
    # Date
    disable_weekend = models.BooleanField(default=True)
    available_booking_months = models.IntegerField(default=1, help_text="if 2, user can only book booking for next two months.")
    max_booking_per_day = models.IntegerField(null=True, blank=True)
    # Time
    start_time = models.TimeField()
    end_time = models.TimeField()
    period_of_each_booking = models.CharField(max_length=3, default="30", choices=BOOKING_PERIOD, help_text="How long each booking take.")
    max_booking_per_time = models.IntegerField(default=1, help_text="how much booking can be book for each time.")
    shop_profile = models.ForeignKey(ShopProfile,default=None ,on_delete=models.CASCADE, related_name='shop_preferences')

class ShopReview(models.Model):
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    shop_profile = models.ForeignKey(ShopProfile, on_delete=models.CASCADE, related_name='reviews')
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_body = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])

class BarberDetails(models.Model):
    shop_profile = models.ForeignKey(ShopProfile,default=None ,on_delete=models.CASCADE, related_name='barber_details')
    barber_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    barber_name = models.CharField(max_length=70, blank=False)
    phone_number = models.CharField(max_length=15, blank=False)
