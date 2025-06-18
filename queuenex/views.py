from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator as custom_token_generator
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import UserRegisteration
from rest_framework import status

import os
# Create your views here.
from django.shortcuts import render

from .serializers import *
from urllib.parse import quote
from django.core.mail import send_mail
from .models import *
from rest_framework.decorators import api_view, APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
# import stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
@api_view(["POST"])
def register(request):
    
    
    serializer = None

    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    if UserRegisteration.objects.filter(email=email).exists():
        return Response({"error": "Email already registered as user."}, status=status.HTTP_400_BAD_REQUEST)
    
   
    serializer = UserRegisterationSerializer(data=request.data)
    password = request.data.get('password')
    password_confirmation = request.data.get('confrmpassword')

    if password != password_confirmation:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

   
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["POST"])
def login(request):

    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
       
       
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        request.session['user_id'] = user.id
        request.session['user_email'] = user.email
       
 
        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'role': user.role,
            'user_id': user.id,
            'email':user.email,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'detail': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)












# @api_view(['POST',])
# def admin_login(request):
#      username=request.data.get("username")
#      password=request.data.get("password")
#      if not username or not password:
#         return Response({'detail': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

#      user = authenticate(username=username, password=password)

#      if user is None:
#         return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)

#      if not user.is_staff:
#         return Response({'detail': 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)

#      return Response({'detail': 'Login successful!','username': user.username }, status=status.HTTP_200_OK)


# @api_view(["POST"])
# def contactus(request):
#     serializer = ContactSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({
#       "message": "Thank you for contacting us.",
#       "data": serializer.data
#  }, status=status.HTTP_201_CREATED)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# @api_view(["GET"])
# def get_all_msgs(request):
 
#    if request.method == "GET":
#         contact = ContactUs.objects.all()
#         serializer = ContactSerializer(contact,many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class CreatePaymentIntentView(APIView):
#     def post(self, request, *args, **kwargs):
     
#         serializer = PaymentIntentSerializer(data=request.data)
#         if serializer.is_valid():
#             payment_id = serializer.validated_data['payment_id']
#             amount = serializer.validated_data['amount']
       

#             try:
            
#                 payment_intent = stripe.PaymentIntent.create(
#                     amount=amount,
#                     currency="eur",
#                     payment_method=payment_id,
                    
#                     confirmation_method='manual',
#                     confirm=True, 
#                     return_url = f"{request.scheme}://{request.get_host()}/payment-success/"
#                 )

                
#                 return Response(
#                     {'clientSecret': payment_intent.client_secret},
#                     status=status.HTTP_200_OK
#                 )
#             except stripe.error.CardError as e:
#                 # Handle card errors
#                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#             except Exception as e:
#                 return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def password_reset(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required."}, status=400)

    try:
        user = UserRegisteration.objects.get(email=email)
    except UserRegisteration.DoesNotExist:
        return Response({"error": "User not found."}, status=400)

    signer = TimestampSigner()
    signed_token = signer.sign(user.email)
    encoded_token = quote(signed_token)

    reset_link = f'http://localhost:5173/reset-password?token={encoded_token}'
    from_email = os.getenv('DEFAULT_FROM_EMAIL', 'support@raftersfoodservices.ie')

    send_mail(
        subject='Password Reset Request',
        message=f'Click the following link to reset your  account password: {reset_link}',
        from_email=from_email,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return Response({"message": "Password reset email sent."}, status=200)
@api_view(["POST"])
def password_reset_confirm(request):
    token = request.data.get("token")
    new_password = request.data.get("new_password")
    confirm_password = request.data.get("confirm_password")

    if not token or not new_password or not confirm_password:
        return Response({"error": "Token, new password, and confirm password are required."}, status=400)

    if new_password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=400)

    try:
        signer = TimestampSigner()
        email = signer.unsign(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        return Response({"error": "Invalid or expired token."}, status=400)

    try:
        user = UserRegisteration.objects.get(email=email)
    except UserRegisteration.DoesNotExist:
        return Response({"error": "User not found."}, status=400)

    # Don't hash here, let model's save() do it
    user.password = new_password
    user.confrmpassword = new_password
    user.save()

    return Response({"message": "Password reset successful."}, status=200)
