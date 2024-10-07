from django.db import models
import uuid

# Create your models here.
class userModel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    email = models.EmailField()
    age = models.IntegerField()
    phoneNumber = models.CharField(max_length=20)
    #location = models.CharField(max_length=255)


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique user_id as primary key
    email = models.EmailField(unique=True)  # Ensure email is unique
    mobile_number = models.CharField(max_length=15, unique=True)  # Ensure mobile number is unique
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.email} ({self.user_id})'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email}'s profile"