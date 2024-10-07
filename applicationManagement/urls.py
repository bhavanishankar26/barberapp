from django.urls import path
from . import views

urlpatterns = [
    path("shop/<uuid:shop_id>/services",views.list_shop_services,name="barber_shops"),
    path('shop/<uuid:shop_id>/reviews', views.list_reviews, name='list_reviews'),
    path('get_shops_nearby/', views.get_shops_nearby, name='get_shops_nearby'),
    path('shop/<uuid:shop_id>/get_shop_details',views.get_shop_details, name='get_shop_details')
]
