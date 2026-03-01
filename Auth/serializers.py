from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer , TokenRefreshSerializer

from .models import User, AccountTypes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

# class AccountSerializer(serializers.ModelSerializer):

#     email = serializers.EmailField(read_only=True)

#     role = serializers.ChoiceField(choices=AccountTypes.choices)

#     registration_method = serializers.CharField(read_only=True)

#     email_verified = serializers.BooleanField(read_only=True)

#     rest_code = serializers.CharField(read_only=True)
#     rest_code_expires = serializers.DateTimeField(
#         format="%Y-%m-%dT%H:%M:%SZ",
#         read_only=True
#     )

#     class Meta:
#         model = User

#         fields = [
#             'id',

#             # Auth
#             'email',
#             'role',
#             'registration_method',
#             'email_verified',

#             # Profile
#             'whatsapp_number',
#             'profile_picture',

#             # Password reset
#             'rest_code',
#             'rest_code_expires',

#             # Django fields
#             'is_active',
#             'is_staff',
#             'date_joined',
#             'last_login',
#             'first_name',
#             'last_name',

#         ]

#         read_only_fields = [
#             'id',
#             'email',
#             'role',
#             'registration_method',
#             'email_verified',
#             'rest_code',
#             'rest_code_expires',
#             'is_active',
#             'is_staff',
#             'date_joined',
#             'last_login',
#         ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  

    @classmethod
    def get_token(cls, user):
       
        token = super().get_token(user)

        
        token['role'] = user.role  
        return token
    
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs['refresh'])
            data = {}
            access_token = refresh.access_token

            # Get user from user_id claim inside the refresh token
            user_id = refresh['user_id']
            user = User.objects.get(id=user_id)

            # Add custom claims
            access_token['role'] = user.role
            # Return both tokens
            data['access'] = str(access_token)
            data['refresh'] = str(refresh)

            return data

        except TokenError as e:
            raise InvalidToken(e.args[0])

