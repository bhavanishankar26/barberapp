import datetime
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from common.utils import get_status_string

from .models import Booking, BookingService, ShopBookingsCounter
from shopManagement.models import ShopProfile, ShopService, ShopSettings
from rest_framework.response import Response
from rest_framework import status 
from django.db import transaction
from datetime import date
from usermanagement.models import userModel

def add_delta(time: datetime.time, delta: datetime.datetime) -> datetime.time:
    # transform to a full datetime first
    return (datetime.datetime.combine(
        datetime.date.today(), time
    ) + delta).time()

# this is invoked when user tries to click on barber tile for available slots
@api_view(('GET',))
def barber_available_slots(request, shop_id):
    try:
        date = request.data.get('date')
        
        # Validate shop profile
        shop_profile = ShopProfile.objects.filter(shop_id=shop_id).first()
        if not shop_profile:
            return Response({'message': "Shop profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate booking settings for the shop
        booking_settings = ShopSettings.objects.filter(shop_profile=shop_profile).first()
        if not booking_settings:
            return Response({'message': "Barber Booking Settings Not Configured Yet.."}, status=status.HTTP_400_BAD_REQUEST)

        existing_bookings_time_freq_list = ShopBookingsCounter.objects.filter(
                                            booking_date = date, 
                                            shop_profile = shop_profile
                                            ).values_list('booking_time','num_of_bookings').order_by('booking_time')
        if len(existing_bookings_time_freq_list) == 0:
            return Response({'message':"No Bookings found for the Date provided.."},status=status.HTTP_200_OK)
        
        time_freq_map = {}
        for time,num_of_bookings in existing_bookings_time_freq_list:
            time_freq_map[str(time)] = num_of_bookings
        booking_settings_start_time =  booking_settings.start_time
        booking_settings_max_bookings_per_time =  booking_settings.max_booking_per_time
        booking_settings_period_of_each_booking = booking_settings.period_of_each_booking
        booking_settings_end_time = booking_settings.end_time
        next_time = booking_settings_start_time
        time_list = []
        while True:
            curr_available_time_existing_freq = 0 if time_freq_map.get(str(next_time)) is None else time_freq_map.get(str(next_time))
            remaining_slots = booking_settings_max_bookings_per_time - curr_available_time_existing_freq 

            if booking_settings_max_bookings_per_time <= curr_available_time_existing_freq:
                remaining_slots = 0

            time_list.append(
                {"time": ":".join(str(next_time).split(":")[:-1]), "remaining_slots": remaining_slots})
            next_time = add_delta(next_time, datetime.timedelta(
                minutes=int(booking_settings_period_of_each_booking)))
            if next_time > booking_settings_end_time:
                break
        return Response({'message':"available booking slots",'time_list':time_list},status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response({'Internal server error ': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(('POST',))
def create_booking(request, shop_id):
    try:
        # Extract data from request
        service_ids = request.data.get('service_ids', [])
        date = request.data.get('date')
        time = request.data.get('time')
        user_id = request.data.get('user_id')
        total_cost = request.data.get('total_price')

        # Validate shop profile
        shop_profile = ShopProfile.objects.filter(shop_id=shop_id).first()
        if not shop_profile:
            return Response({'message': "Shop profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate booking settings for the shop
        booking_settings = ShopSettings.objects.filter(shop_profile=shop_profile).first()
        if not booking_settings:
            return Response({'message': "Barber Booking Settings Not Configured Yet.."}, status=status.HTTP_400_BAD_REQUEST)

        # Check existing bookings for the same date and time
        curr_time_barber_bookings = ShopBookingsCounter.objects.filter(
            booking_date=date, shop_profile=shop_profile, booking_time=time).first()

        if curr_time_barber_bookings is None:
            curr_time_freq = 1
        else:
            curr_time_freq = curr_time_barber_bookings.num_of_bookings + 1

        booking_settings_max_bookings_per_time = booking_settings.max_booking_per_time

        # If there's an available slot
        if booking_settings_max_bookings_per_time >= curr_time_freq:
            with transaction.atomic():
                # Create a booking for each service_id
                for service_id in service_ids:
                    service = ShopService.objects.filter(service_id=service_id, shop_profile=shop_profile).first()
                    if not service:
                        return Response({'message': f"Service with id {service_id} not found for this shop."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    # Create the booking
                    booking = Booking(
                        user_id=user_id,
                        status='0',
                        shop_profile=shop_profile,
                        booking_date=datetime.datetime.strptime(date, "%Y-%m-%d").date(),
                        booking_time=time,
                        total_price = total_cost
                    )
                    created_booking = booking.save()

                    # Payment API here - and update to "failed" after this if needed

                    # Link the service to the booking in BookingService
                    booking_service = BookingService(booking=booking, shop_service=service)
                    booking_service.save()

                # Handle booking counter
                if curr_time_barber_bookings is None:
                    # Create a new booking counter if it doesn't exist
                    barber_booking_counter = ShopBookingsCounter(
                        booking_date=datetime.datetime.strptime(date, "%Y-%m-%d").date(),
                        booking_time=time,
                        shop_profile=shop_profile,
                        num_of_bookings=curr_time_freq
                    )
                    barber_booking_counter.save()
                else:
                    # Update the existing booking counter
                    curr_time_barber_bookings.num_of_bookings = curr_time_freq
                    curr_time_barber_bookings.save()

            return Response({'message': "Booking Confirmed"}, status=status.HTTP_201_CREATED)

        # No slots available
        return Response({'message': "No Slots Available for the selected time"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Booking Statuses for a transaction.
# 0 - Booked
# 1 - Completed
# 2 - Cancelled 
# 3 - Failed
# Bookings can only be cancelled i.e. "2" when they are in Booked status i.e. "0". 


@api_view(['POST'])
def update_booking_status(request):
    try:
        # Get booking_id and status from request
        booking_id = request.data.get('booking_id')
        new_status = request.data.get('status')
        # Validate inputs
        if not booking_id or not new_status:
            return Response({"error": "booking_id and status are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the booking by id
        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure booking status is "Booked" before allowing an update
        if booking.status != '0':
            return Response({"error": "Booking status can only be updated if the current status is 'Booked'."}, status=status.HTTP_400_BAD_REQUEST)

        # Update booking status to 'Completed' or 'Cancelled'
        if new_status in ['1', '2']:
            booking.status = new_status
            booking.save()
            booking_status_string = get_status_string(new_status)
            if new_status == '2':
                booking_date = booking.booking_date
                booking_time = booking.booking_time
                shop_profile = booking.shop_profile
                curr_time_barber_bookings = ShopBookingsCounter.objects.filter(
                                                                booking_date=booking_date, 
                                                                shop_profile=shop_profile, 
                                                                booking_time=booking_time).first()
                curr_time_barber_bookings.num_of_bookings = curr_time_barber_bookings.num_of_bookings - 1
                curr_time_barber_bookings.save()

            return Response({"message": f"Booking status updated to '{booking_status_string}'."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid status. Status can only be 'Completed' or 'Cancelled'."}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Get all the list of bookings for a particular shop for that day
@api_view(['GET'])
def get_upcoming_bookings(request, shop_id):

    try:
        # Get today's date if not provided in request
        booking_date = request.data.get('date', datetime.date.today().strftime('%Y-%m-%d'))
        booking_status = request.GET.get('status', None)
        # print("Booking Status : ", booking_status)

        if booking_status in [None, '']:
            return Response({'message': "No Booking Status provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the shop profile
        shop_profile = ShopProfile.objects.filter(shop_id=shop_id).first()
        if not shop_profile:
            return Response({'message': "Shop profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not ['1', '2', '3', '4']:
            return Response({'message': "Invalid Booking Status provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all bookings for the shop on the specified date
        bookings = Booking.objects.filter(shop_profile=shop_profile, booking_date=booking_date, status = booking_status).order_by('booking_time')

        if not bookings.exists():
            return Response({'message': f"No bookings found for {booking_date}."}, status=status.HTTP_200_OK)

        # Prepare the booking details to return
        booking_list = []
        for booking in bookings:
            booking_list.append({
                "booking_id": str(booking.booking_id),
                "user_id": booking.user_id,
                "status": booking.status,
                "booking_time": booking.booking_time.strftime("%H:%M"),
                "created_at": booking.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": booking.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "shop_service": booking.shop_service.name if booking.shop_service else None,
                "total_price" : booking.total_price
            })

        return Response({'message': "Upcoming bookings", 'bookings': booking_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': "Internal server error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)