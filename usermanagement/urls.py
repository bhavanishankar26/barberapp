from django.contrib import admin
from django.urls import path
from .views import register_user, create_user_profile, update_user_profile


urlpatterns = [
    path('register/', register_user, name='register_user'),
    
    path('<uuid:user_id>/profile/create/', create_user_profile, name='create_user_profile'),
    
    # API to update a user profile
    path('<uuid:user_id>/profile/update/', update_user_profile, name='update_user_profile'),
]
