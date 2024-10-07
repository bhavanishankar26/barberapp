from django.contrib import admin
from django.urls import path
from .views import add_service, create_shop_profile, create_shop_preferences, update_shop_preferences,update_service, add_review, update_shop_profile
from .views import *

urlpatterns = [
    path('create-profile', create_shop_profile,name='shop-profile-create'),
    path('<uuid:shop_id>/update-profile', update_shop_profile, name = 'shop-profile-update'),
    path('<uuid:shop_id>/add-service',  add_service, name = 'add_barber_service'),
    path('<uuid:shop_id>/add-review', add_review, name = 'add_shop_review'),
    path('<uuid:shop_id>/create-preferences',create_shop_preferences, name = 'create-shop-preferences'),
    path('<uuid:shop_id>/update-preferences',update_shop_preferences, name = 'update-shop-preferences'),
    path('<uuid:shop_id>/service/<uuid:service_id>/update-service',update_service, name = "update_barber_service"),
    path('<uuid:shop_id>/earnings', get_shop_earnings, name='shop-earnings'),
    path('<uuid:shop_id>/disable-slot',disable_time_slot,name = 'disable_time_slot'),
    path('<uuid:shop_id>/create-barber-details', create_barber_details, name = 'create_barber_details')
]
