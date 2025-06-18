from .models import *
from rest_framework import serializers
from django.contrib.auth.hashers import check_password 

class UserRegisterationSerializer(serializers.ModelSerializer):
 
   
    class Meta:
        model = UserRegisteration
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    role = serializers.ChoiceField(choices=UserRegisteration.ROLE_CHOICES)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        try:
            user = UserRegisteration.objects.get(email=email, role=role)
        except UserRegisteration.DoesNotExist:
            raise serializers.ValidationError("Invalid email or role.")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid password.")

        data['user'] = user
        return data
# class ContactSerializer(serializers.ModelSerializer):
 
   
#     class Meta:
#         model = ContactUs
#         fields = '__all__'

# class PaymentIntentSerializer(serializers.Serializer):
#     payment_id = serializers.CharField() 
#     amount = serializers.IntegerField()  
    