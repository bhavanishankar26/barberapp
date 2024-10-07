from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.core.exceptions import ValidationError

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from shopManagement.models import ShopProfile, ShopReview, ShopService, ShopServicesImage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from geopy.distance import geodesic
from decimal import Decimal, InvalidOperation

import math
import logging

# Configure logging for error tracking
logger = logging.getLogger(__name__)
from drf_spectacular.utils import extend_schema, OpenApiParameter

@api_view(['GET'])
def list_reviews(request, shop_id):
    try:
        shop_profile = ShopProfile.objects.get(shop_id=shop_id)
        reviews = ShopReview.objects.filter(shop_profile = shop_profile)
        # Pagination parameters
        page = int(request.GET.get('page', 1))  # Default to page 1 if no page parameter is provided
        per_page = int(request.GET.get('per_page', 10)) # Default to 10 reviews per page if not provided
        
        total_reviews = reviews.count()
        start = (page - 1) * per_page
        end = start + per_page

        # Slice the queryset for the current page
        paginated_reviews = reviews[start:end]
    
        # Manually construct the response data
        reviews_data = []
        for review in paginated_reviews:
           
            reviews_data.append({
                'review_id': review.review_id,
                'review_body': review.review_body,
                'review_rating': review.rating,
            })

        # Calculate pagination metadata
        total_pages = (total_reviews + per_page - 1) // per_page  # Ceiling division

        response_data = {
            'count': total_reviews,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'results': reviews_data
        }

        return JsonResponse(response_data)

    except ShopProfile.DoesNotExist:
        return JsonResponse({"error": "Shop profile not found."}, status=404)
    except Exception as e:
        # Log the exception if needed
        # log.exception("Error occurred in list_reviews view: %s", e)
        return JsonResponse({"error": "An unexpected error occurred. Please try again later."}, status=500)

@api_view(['GET'])
def list_shop_services(request, shop_id):
    try:
        # Retrieve the ShopProfile by shop_id
        shop_profile = ShopProfile.objects.get(shop_id=shop_id)
        
        # Get page and per_page parameters from request query params
        page = int(request.GET.get('page', 1))  # Default to page 1 if not provided
        per_page = int(request.GET.get('per_page', 10))  # Default to 10 items per page

        # Filter the services related to the shop profile
        services = ShopService.objects.filter(shop_profile=shop_profile)

        # Implement custom pagination
        total_services = services.count()
        start = (page - 1) * per_page
        end = start + per_page

        # Slice the queryset for the current page
        paginated_services = services[start:end]

        # Manually construct the response data
        services_data = []
        for service in paginated_services:
            images = ShopServicesImage.objects.filter(service=service)
            images_data = [{'image_url': request.build_absolute_uri(img.image.url), 'description': img.description} for img in images]

            services_data.append({
                'service_id': service.service_id,
                'service_name': service.name,
                'description': service.description,
                'price': str(service.price),
                'duration_in_secs': service.duration,
                'images': images_data
            })

        # Calculate pagination metadata
        total_pages = (total_services + per_page - 1) // per_page  # Ceiling division

        response_data = {
            'count': total_services,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page,
            'results': services_data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ShopProfile.DoesNotExist:
        return Response({"error": "ShopProfile not found."}, status=status.HTTP_404_NOT_FOUND)
    

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in kilometers between two points on the earth (specified in decimal degrees)"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km

@api_view(['GET'])
def get_shops_nearby(request):
    try:
        # Retrieve latitude and longitude from the request
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        # Convert to Decimal and validate
        if latitude and longitude:
            try:
                latitude = Decimal(latitude)
                longitude = Decimal(longitude)
            except InvalidOperation:
                return Response({"error": "Invalid latitude or longitude format."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Latitude and longitude are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find shops within 5 km radius
        nearby_shops = []
        user_location = (latitude, longitude)

        for shop in ShopProfile.objects.all():
            shop_location = (shop.latitude, shop.longitude)
            if shop.latitude and shop.longitude:  # Ensure shop has latitude and longitude
                distance = geodesic(user_location, shop_location).kilometers
                if distance <= 5:
                    nearby_shops.append({
                        "shop_id": shop.shop_id,
                        "shop_name": shop.shop_name,
                        "about_us": shop.about_us,
                        "email": shop.email,
                        "phone_number": shop.phone_number,
                        "address": shop.address,
                        "latitude": str(shop.latitude),
                        "longitude": str(shop.longitude),
                        "distance_km": round(distance, 2)
                    })

        return Response({"nearby_shops": nearby_shops}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_shop_details(request, shop_id):
    try:
        # Fetch the shop profile by shop_id
        shop_profile = ShopProfile.objects.filter(shop_id=shop_id).first()
        if not shop_profile:
            return Response({"error": "Shop profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Split venue_amenities on the colon and return as a list
        venue_amenities_list = shop_profile.venue_amenities.split(':') if shop_profile.venue_amenities else []

        # Build the response data
        shop_data = {
            "about_us": shop_profile.about_us,
            "phone_number": shop_profile.phone_number,
            "venue_amenities": venue_amenities_list,
        }

        return Response(shop_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)