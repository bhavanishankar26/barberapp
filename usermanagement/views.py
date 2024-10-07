from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, UserProfile
from django.db import IntegrityError
# import boto3
# from botocore.exceptions import ClientError
# import os

@api_view(['POST'])
def register_user(request):
    # Get email and mobile_number from request
    email = request.data.get('email')
    mobile_number = request.data.get('mobile_number')

    # Check if all required fields are provided
    if not email or not mobile_number:
        return Response({'message': "Email and mobile_number are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new user
    try:
        user = User(email=email, mobile_number=mobile_number)
        user.save()  # Save the user, which automatically generates a unique user_id
        return Response({
            'message': 'User registered successfully',
            'user_id': str(user.user_id)  # Return the unique user_id in the response
        }, status=status.HTTP_201_CREATED)

    except IntegrityError:
        return Response({'message': 'Email or Mobile number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'message': f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # Initialize Cognito client
# client = boto3.client('cognito-idp', region_name='your-region')

# @api_view(['POST'])
# def initiate_auth(request):
#     username = request.data.get('username')  # Can be email or mobile
#     if not username:
#         return Response({'message': "Username (email or mobile number) is required."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         # Initiate auth with Cognito (username = email or mobile)
#         response = client.initiate_auth(
#             AuthFlow='CUSTOM_AUTH',
#             AuthParameters={'USERNAME': username},
#             ClientId=os.environ.get('COGNITO_CLIENT_ID')  # Cognito App Client ID
#         )
#         return Response({'message': 'OTP sent to user', 'Session': response['Session']}, status=status.HTTP_200_OK)
#     except ClientError as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def verify_otp(request):
#     username = request.data.get('username')
#     otp = request.data.get('otp')
#     session = request.data.get('session')  # Session from `initiate_auth`

#     if not all([username, otp, session]):
#         return Response({'message': 'Username, OTP, and session are required.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         # Respond to OTP challenge with Cognito
#         response = client.respond_to_auth_challenge(
#             ClientId=os.environ.get('COGNITO_CLIENT_ID'),
#             ChallengeName='CUSTOM_CHALLENGE',
#             Session=session,
#             ChallengeResponses={
#                 'USERNAME': username,
#                 'ANSWER': otp  # The OTP entered by the user
#             }
#         )

#         if 'AuthenticationResult' in response:
#             # Authentication was successful
#             auth_result = response['AuthenticationResult']
#             return Response({
#                 'message': 'Authentication successful',
#                 'AccessToken': auth_result['AccessToken'],
#                 'IdToken': auth_result['IdToken'],
#                 'RefreshToken': auth_result['RefreshToken']
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({'message': 'Authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

#     except ClientError as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_user_profile(request, user_id):
    try:
        # Fetch the user by user_id
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if the profile already exists
    if UserProfile.objects.filter(user=user).exists():
        return Response({"error": "Profile already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create a new user profile
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    profile_picture = request.FILES.get('profile_picture')  # Handle profile picture upload

    # Create the UserProfile instance
    user_profile = UserProfile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        profile_picture=profile_picture
    )

    return Response({
        "message": "Profile created successfully",
        "first_name": user_profile.first_name,
        "last_name": user_profile.last_name,
        "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None
    }, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
def update_user_profile(request, user_id):
    try:
        # Fetch the user by user_id
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Fetch the existing profile
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)

    # Update user profile fields
    if 'first_name' in request.data:
        user_profile.first_name = request.data.get('first_name')
    if 'last_name' in request.data:
        user_profile.last_name = request.data.get('last_name')
    if 'profile_picture' in request.FILES:
        user_profile.profile_picture = request.FILES.get('profile_picture')
    
    # Save the updated profile
    user_profile.save()
    
    return Response({
        "message": "Profile updated successfully",
        "first_name": user_profile.first_name,
        "last_name": user_profile.last_name,
        "profile_picture": user_profile.profile_picture.url if user_profile.profile_picture else None
    }, status=status.HTTP_200_OK)