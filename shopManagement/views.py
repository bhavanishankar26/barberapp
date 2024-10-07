# views.py
from django.http import HttpResponseBadRequest
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from bookingManagement.models import Booking
from .models import BarberDetails, ShopService, ShopProfile, ShopProfileImage, ShopReview, ShopServicesImage, ShopSettings

from django.core.exceptions import ValidationError
from datetime import datetime
from datetime import timedelta
from decimal import Decimal, InvalidOperation
import uuid
from drf_spectacular.utils import extend_schema, OpenApiParameter
from bookingManagement.models import ShopBookingsCounter

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_shop_profile(request):
    shop_name = request.data.get('shop_name')
    about_us = request.data.get('about_us')
    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    address = request.data.get('address')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    images = request.FILES.getlist('images')  # Handle multiple images
    amenities_list = request.data.getlist('venue_amenities')  # Get the list of amenities

    if not all([shop_name, about_us, email, phone_number , address]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
         # Convert latitude and longitude to Decimal if provided
        latitude = Decimal(latitude) if latitude else None
        longitude = Decimal(longitude) if longitude else None

        # Join the amenities list into a single string delimited by ':'
        venue_amenities = ':'.join(amenities_list) if amenities_list else ''
        
        # Create a new shop profile
        shop_profile = ShopProfile.objects.create(
            shop_name=shop_name,
            about_us=about_us,
            email=email,
            phone_number=phone_number,
            address=address,
            latitude=latitude,
            longitude=longitude,
            venue_amenities=venue_amenities
        )

        # Save images if provided
        if images:
            for image in images:
                new_image_id = uuid.uuid4()
                ShopProfileImage.objects.create(image_id = new_image_id, shop_profile=shop_profile, image=image)

        return Response({"message": "Shop profile created successfully.", "shop_id": shop_profile.shop_id},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_shop_profile(request, shop_id):
    shop_name = request.data.get('shop_name')
    about_us = request.data.get('about_us')
    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    address = request.data.get('address')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    images = request.FILES.getlist('images')  # Handle multiple images
    amenities_list = request.data.getlist('venue_amenities')

    if not shop_id:
        return Response({"error": "Shop ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve the shop profile by shop_id
        shop_profile = ShopProfile.objects.filter(shop_id=shop_id).first()
        if not shop_profile:
            return Response({"error": "Shop profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update fields if provided in the request
        if shop_name:
            shop_profile.shop_name = shop_name
        if about_us:
            shop_profile.about_us = about_us
        if phone_number:
            shop_profile.phone_number = phone_number
        if email:
            shop_profile.email = email
        if address:
            shop_profile.address = address
        if latitude:
            try:
                shop_profile.latitude = Decimal(latitude)
            except InvalidOperation:
                return Response({"error": "Invalid latitude format."}, status=status.HTTP_400_BAD_REQUEST)
        if longitude:
            try:
                shop_profile.longitude = Decimal(longitude)
            except InvalidOperation:
                return Response({"error": "Invalid longitude format."}, status=status.HTTP_400_BAD_REQUEST)

        # Join the amenities list into a single string delimited by ':'
        if amenities_list:
            shop_profile.venue_amenities = ':'.join(amenities_list)
        
        # Save the updated shop profile
        shop_profile.save()

        # Update images if provided
        if images:
            ShopProfileImage.objects.filter(shop_profile=shop_profile).delete()  # Remove old images
            for image in images:
                new_image_id = uuid.uuid4()
                ShopProfileImage.objects.create(image_id=new_image_id, shop_profile=shop_profile, image=image)

        return Response({"message": "Shop profile updated successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
@api_view(['POST'])
def add_service(request, shop_id):
    try:
        shop_profile = ShopProfile.objects.filter(shop_id=shop_id).first()
        
        name = request.data.get('name')
        description = request.data.get('description')
        price = request.data.get('price')
        duration = request.data.get('duration')
        images = request.FILES.getlist('images')
        
        if not name or not price or not duration:
            return HttpResponseBadRequest("Name, price, and duration are required fields.")
        
        try:
            price = float(price)
            duration = int(duration)  # Duration in minutes
        except ValueError:
            return HttpResponseBadRequest("Invalid price or duration format.")
        
        # Convert duration from minutes to a timedelta object
        from datetime import timedelta
        duration_timedelta = timedelta(minutes=duration)
        new_service_id = uuid.uuid4()
        # Create the service
        ShopService.objects.create(
            service_id = new_service_id,
            shop_profile=shop_profile,
            name=name,
            description=description,
            price=price,
            duration=duration_timedelta
        )
        if images:
            new_image_id = uuid.uuid4()
            shop_service = ShopService.objects.get( service_id = new_service_id)
            for image in images:
                ShopServicesImage.objects.create(image_id = new_image_id,service = shop_service, image=image)
        return Response({"message": "Shop service created successfully.", "shop_id": shop_profile.shop_id,"service_id":new_service_id},
                    status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def add_review(request, shop_id):
    try:
        shop_profile = ShopProfile.objects.get(shop_id=shop_id)
        
        review_body = request.data.get('review_body')
        rating = request.data.get('rating')
        if not review_body or not rating:
            return HttpResponseBadRequest("Review body and rating are required fields.")
        rating = int(rating)
        if rating < 1 or rating > 5:
            return HttpResponseBadRequest("Rating must be between 1 and 5.")

        # Create the review
        ShopReview.objects.create(
            shop_profile=shop_profile,
            # TODO: for now hard coded userid
            # user= "123",
            review_body=review_body,
            rating=rating
        )
        
        return Response({"message": "Review Added Successfully!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_service(request, shop_id, service_id):
    try:
        
        # Validate and fetch ShopProfile
        try:
            shop_profile = ShopProfile.objects.get(shop_id=shop_id)
        except ShopProfile.DoesNotExist:
            return Response({"error": "ShopProfile with the provided shop_id does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the existing ShopService record
        try:
            service = ShopService.objects.get(service_id=service_id)
        except ShopService.DoesNotExist:
            return Response({"error": "Service with the provided service_id does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields if provided
        name = request.data.get('name')
        description = request.data.get('description')
        price = request.data.get('price')
        duration = request.data.get('duration')
        
        if name is not None:
            service.name = name
        if description is not None:
            service.description = description
        if price is not None:
            try:
                service.price = float(price)
            except ValueError:
                return Response({"error": "Invalid price format."}, status=status.HTTP_400_BAD_REQUEST)
        if duration is not None:
            try:
                duration = int(duration)  # Duration in minutes
                service.duration = timedelta(minutes=duration)
            except ValueError:
                return Response({"error": "Invalid duration format."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure the service is associated with the correct ShopProfile
        service.shop_profile = shop_profile
        service.save()
        
        return Response({
            "message": "Shop service updated successfully.",
            "service_id": service.service_id,
            "shop_id": service.shop_profile.shop_id,
            "name": service.name,
            "description": service.description,
            "price": service.price,
            "duration": str(service.duration)
        }, status=status.HTTP_200_OK)
    
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_shop_preferences(request, shop_id):
    # Extracting data from request
    booking_enable = request.data.get('booking_enable')
    confirmation_required = request.data.get('confirmation_required')
    disable_weekend = request.data.get('disable_weekend')
    available_booking_months = request.data.get('available_booking_months')
    max_booking_per_day = request.data.get('max_booking_per_day')
    start_time_str = request.data.get('start_time')
    end_time_str = request.data.get('end_time')
    period_of_each_booking = request.data.get('period_of_each_booking')
    max_booking_per_time = request.data.get('max_booking_per_time')

    # Check if all mandatory fields are provided
    required_fields = [
        'booking_enable', 'confirmation_required', 'disable_weekend',
        'available_booking_months', 'max_booking_per_day', 'start_time',
        'end_time', 'period_of_each_booking', 'max_booking_per_time'
    ]
    
    missing_fields = [field for field in required_fields if field not in request.data]
    if missing_fields:
        return Response({'error': f'Missing fields: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate field types and values
    try:
        available_booking_months = int(available_booking_months)
        max_booking_per_day = int(max_booking_per_day)
        max_booking_per_time = int(max_booking_per_time)
        # Parse time fields
        start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
        end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
        period_of_each_booking = str(period_of_each_booking)

        # Validate `shop_id` and fetch ShopProfile
        shop_profile = ShopProfile.objects.get(shop_id=shop_id)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid data format or type.'}, status=status.HTTP_400_BAD_REQUEST)
    except ShopProfile.DoesNotExist:
        return Response({'error': 'ShopProfile with the provided shop_id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if ShopSettings with the same shop_id already exists
    if ShopSettings.objects.filter(shop_profile=shop_profile).exists():
        return Response({'error': 'A ShopSettings record with this shop_id already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create ShopSettings instance
    try:
        shop_settings = ShopSettings.objects.create(
            shop_profile = shop_profile,
            booking_enable=booking_enable,
            confirmation_required=confirmation_required,
            disable_weekend=disable_weekend,
            available_booking_months=available_booking_months,
            max_booking_per_day=max_booking_per_day,
            start_time=start_time,
            end_time=end_time,
            period_of_each_booking=period_of_each_booking,
            max_booking_per_time=max_booking_per_time
        )
        return Response({
            'booking_enable': shop_settings.booking_enable,
            'confirmation_required': shop_settings.confirmation_required,
            'disable_weekend': shop_settings.disable_weekend,
            'available_booking_months': shop_settings.available_booking_months,
            'max_booking_per_day': shop_settings.max_booking_per_day,
            'start_time': shop_settings.start_time.isoformat(),
            'end_time': shop_settings.end_time.isoformat(),
            'period_of_each_booking': shop_settings.period_of_each_booking,
            'max_booking_per_time': shop_settings.max_booking_per_time,
            'shop_id': shop_id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_shop_preferences(request, shop_id):
    
    # Check if all mandatory fields are provided
    if not shop_id:
        return Response({'error': 'shop_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate `shop_id` and fetch ShopProfile
    try:
        shop_profile = ShopProfile.objects.get(shop_id=shop_id)
    except ShopProfile.DoesNotExist:
        return Response({'error': 'ShopProfile with the provided shop_id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if ShopSettings with the same shop_id exists
    try:
        shop_settings = ShopSettings.objects.get(shop_profile=shop_profile)
    except ShopSettings.DoesNotExist:
        return Response({'error': 'ShopSettings with the provided shop_id does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    # Update ShopSettings instance with provided data
    if 'booking_enable' in request.data:
        shop_settings.booking_enable = request.data.get('booking_enable')
    if 'confirmation_required' in request.data:
        shop_settings.confirmation_required = request.data.get('confirmation_required')
    if 'disable_weekend' in request.data:
        shop_settings.disable_weekend = request.data.get('disable_weekend')
    if 'available_booking_months' in request.data:
        shop_settings.available_booking_months = int(request.data.get('available_booking_months'))
    if 'max_booking_per_day' in request.data:
        shop_settings.max_booking_per_day = int(request.data.get('max_booking_per_day'))
    if 'start_time' in request.data:
        start_time_str = request.data.get('start_time')
        shop_settings.start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
    if 'end_time' in request.data:
        end_time_str = request.data.get('end_time')
        shop_settings.end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
    if 'period_of_each_booking' in request.data:
        shop_settings.period_of_each_booking = str(request.data.get('period_of_each_booking'))
    if 'max_booking_per_time' in request.data:
        shop_settings.max_booking_per_time = int(request.data.get('max_booking_per_time'))

    # Save updated ShopSettings
    try:
        shop_settings.save()
        return Response({
            'id': shop_settings.id,
            'booking_enable': shop_settings.booking_enable,
            'confirmation_required': shop_settings.confirmation_required,
            'disable_weekend': shop_settings.disable_weekend,
            'available_booking_months': shop_settings.available_booking_months,
            'max_booking_per_day': shop_settings.max_booking_per_day,
            'start_time': shop_settings.start_time.strftime('%H:%M:%S'),
            'end_time': shop_settings.end_time.strftime('%H:%M:%S'),
            'period_of_each_booking': shop_settings.period_of_each_booking,
            'max_booking_per_time': shop_settings.max_booking_per_time,
            'shop_id': shop_id
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def disable_time_slot(request,shop_id):
    try:
        # Extract data from the request
        time_str = request.data.get('time')
        
        # Validate time format
        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return Response({'message': "Invalid time format. Use HH:MM."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate shop profile
        shop_profile = ShopProfile.objects.filter(shop_id=shop_id).first()
        if not shop_profile:
            return Response({'message': "Shop profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get today's date
        today = datetime.today().date()

        # Fetch the shop's booking settings
        booking_settings = ShopSettings.objects.filter(shop_profile=shop_profile).first()
        if not booking_settings:
            return Response({'message': "Booking settings not configured for this shop."}, status=status.HTTP_400_BAD_REQUEST)

        max_booking_per_time = booking_settings.max_booking_per_time
        print('max_booking_per_time ',max_booking_per_time)
         # Check if the time slot already exists in the bookings counter
        booking_counter, created = ShopBookingsCounter.objects.get_or_create(
            shop_profile=shop_profile, 
            booking_date=today, 
            booking_time=time_obj
        )
        print('booking_counter ',booking_counter)

        # Update the number of bookings to max_booking_per_time to effectively disable the slot
        booking_counter.num_of_bookings = max_booking_per_time
        booking_counter.save()

        return Response({'message': "Time slot disabled successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_shop_earnings(request, shop_id):
    try:
        # Get the date range for the query (optional query params)
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        print("start date uk: ", start_date_str)
        # If no date is provided, calculate today's earnings by default
        if not start_date_str or not end_date_str:
            today = datetime.today().date()
            start_date = today
            end_date = today
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get the shop profile
        shop_profile = ShopProfile.objects.get(shop_id=shop_id)

        # Retrieve all bookings for the given shop and date range
        bookings = Booking.objects.filter(
            shop_profile=shop_profile,
            booking_date__range=[start_date, end_date]
        )

        # Manually calculate total earnings
        total_earnings = Decimal(0.0)
        for booking in bookings:
            if booking.total_price:  # Ensure the booking has a total_price
                total_earnings += booking.total_price

        return Response({
            'shop_id': shop_id,
            'start_date': start_date,
            'end_date': end_date,
            'total_earnings': round(total_earnings, 2)
        }, status=status.HTTP_200_OK)

    except ShopProfile.DoesNotExist:
        return Response({"error": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def create_barber_details(request, shop_id):
    try:
        # Fetch the shop profile by shop_id
        shop_profile = ShopProfile.objects.get(shop_id=shop_id)
    except ShopProfile.DoesNotExist:
        return Response({"error": "Shop profile not found"}, status=status.HTTP_404_NOT_FOUND)

    # Extract data from the request
    barber_name = request.data.get('barber_name')
    phone_number = request.data.get('phone_number')

    # Validate the inputs
    if not barber_name or not phone_number:
        return Response({"error": "Barber name and phone number are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the phone number already exists for the same shop
    if BarberDetails.objects.filter(shop_profile=shop_profile, phone_number=phone_number).exists():
        return Response({"error": "A barber with this phone number already exists for this shop."}, status=status.HTTP_400_BAD_REQUEST)


    # Create a new barber entry
    try:
        barber_details = BarberDetails.objects.create(
            shop_profile=shop_profile,
            barber_name=barber_name,
            phone_number=phone_number
        )
        return Response({
            "message": "Barber details created successfully",
            "barber_id": str(barber_details.barber_id)
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
