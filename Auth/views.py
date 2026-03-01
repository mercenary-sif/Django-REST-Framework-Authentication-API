from django.forms import ValidationError
from rest_framework.response import Response
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from Auth.emailSender import _send_styled_email
from Auth.serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer
from .models import  AccountTypes, User , REGISTRATION_CHOICES
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
import re
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
def Home(request):

    return Response("Hello world")

# Create new account endpoint , allowed for all users
  
class CreateAccountAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        first_name       = request.data.get('first_name')
        last_name        = request.data.get('last_name')
        email            = request.data.get('email')
        whatsapp_number  = request.data.get('whatsapp_number')
        password         = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        # --- Validate ---
        if not all([first_name,last_name, email, whatsapp_number, password, confirm_password]):
            return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({"message": "The password and password confirmation do not match."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', email):
            return Response({"message": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'^\+\d{10,15}$', whatsapp_number):
            return Response({"message": "Invalid WhatsApp format. Use +1234567890"}, status=status.HTTP_400_BAD_REQUEST)
        

        if User.objects.filter(email=email).exists():
            return Response({"message": "A user with this email address already exists."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            now = timezone.now()

            # --- Create User using Manager ---
            user = User.objects.create_user(
                email=email,
                password=password,

                # Profile
                first_name=first_name,
                last_name=last_name,
                whatsapp_number=whatsapp_number,

                # Role & Method
                role= AccountTypes.MANAGER,
                registration_method=REGISTRATION_CHOICES.Email,

                # Email verification / reset
                rest_code=get_random_string(
                    length=6,
                    allowed_chars='0123456789'
                ),
                rest_code_expires=now + timedelta(minutes=10),
            )
            try:
                # dynamic plaintext content (newlines will be converted to paragraphs)
                notif_content = (
                f"Hello {first_name +' '+ last_name},\n\n"
                f"Your MercenaryDev account has been successfully created , here is your confirmation code :{user.rest_code}\n\n"
                f"Login Email: {user.email}\n\n"
                "If you did not expect this email, please contact support immediately."
            )

                # create notification & send email (send_notification_email will create the Notification if needed)
                send_result = _send_styled_email(
                    to_email=user.email,
                    subject="Welcome to MercenaryDev",
                    title="Account Created Successfully",
                    content_plain=notif_content,
                    recipient_name=user.get_full_name(),
                    action_url=settings.SITE_URL + "/login",
                    action_text="Login Now"
                )

                if not send_result.get("ok"):
                    user.delete()
                    return Response({"message":  "Failed to send confirmation code to email , please try sing up again"}, status=status.HTTP_400_BAD_REQUEST)
            except:
            # don't crash the endpoint if notification fails
                user.delete()
                return Response({"message": "Failed to send confirmation code to email , please try sing up again"}, status=status.HTTP_400_BAD_REQUEST)
    
            return Response({'message': 'New account successfully created',}, status=status.HTTP_200_OK)
        
        except Exception as e:
            user.delete()
            return Response({"message": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
 
class SingInView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        
        if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', email):
            return Response({"message": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not email or not password:
                return Response({'message': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
                user = User.objects.get(email=email)    
        except User.DoesNotExist:
            return Response({'message': 'No account is associated with this email address..!'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
                return Response({'message': 'Incorrect password. please try again'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
                return Response({'message': 'The account is inactive.'}, status=status.HTTP_403_FORBIDDEN)
       
        
        # Now generate tokens using the serializer
        serializer = CustomTokenObtainPairSerializer(data={"email": email, "password": password})
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        return Response({
                'message': 'Connection successful.',
                'tokens': tokens,
            
            }, status=status.HTTP_200_OK)



@api_view(["POST"])
def google_auth(request):
    token = request.data.get("token")
 
    if not token:
        return Response({"error": "Token not provided","status":False}, status=status.HTTP_400_BAD_REQUEST)
    try:
        # Modern approach - verify the token
        id_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_OAUTH_CLIENT_ID,
            clock_skew_in_seconds=10  # Allow for clock skew
        )
        
        # Verify the token issuer
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            return Response(
                {"error": "Invalid token issuer", "status": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract user info
        email = id_info.get('email')
        email_verified = id_info.get('email_verified', False)
        
        if not email_verified:
            return Response(
                {"error": "Email not verified with Google", "status": False},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        profile_pic_url = id_info.get('picture', '')
        google_id = id_info.get('sub')  # Google's unique user ID
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'registration_method': REGISTRATION_CHOICES.Google,
                'email_verified': True,
            }
        )
        

        if created:
            user.set_unusable_password()
            user.save()
        elif not user:
            # Check if user registered via email
            if user.registration_method != REGISTRATION_CHOICES.Google:
                return Response({
                    "error": "This email is registered with email/password. Please sign in using your password.",
                    "status": False
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh.access_token['role'] = user.role
        return Response({
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_picture": profile_pic_url,
            },
            "status": True
        }, status=status.HTTP_200_OK)  
    except ValueError:
        return Response({"error": "Invalid token","status":False}, status=status.HTTP_400_BAD_REQUEST)
    

# Refresh token endpoint
class TokenRefresh(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            # Validate and get tokens
            serializer.is_valid(raise_exception=True)
            tokens = serializer.validated_data

            return Response({
                'message': 'Successful refreshment.',
                'tokens': tokens
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({
                'message': 'The token is invalid or expired.' ,
                'details': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)

        except ValidationError as e:
            return Response({
                'message': 'Token invalid.',
                'details': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        


# confirm mail endpoint
class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        email = request.data.get('email')

        if not code:
            return Response({"message": "Un code de réinitialisation est requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', email):
            return Response({"error": "invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user =  User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found for the email address provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.rest_code != code:
            return Response({"message": "Code invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.rest_code_expires or timezone.now() > user.rest_code_expires:
            return Response({"message": "Le code a expiré."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user.email_verified = True
            user.save()
            return Response({"message": "Email confirmé avec succès."}, status=status.HTTP_200_OK)
        except:
            return Response({"message": f"Problems on the server"}, status=status.HTTP_400_BAD_REQUEST)  


# reset code for changing the password or during the creation of account for confirming the email  
class RequestResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
       
        email            = request.data.get('email')
        if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', email):
            return Response({"error": "invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
      
        
        try:
            user =  User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found for the email address provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:

            code = get_random_string(length=6, allowed_chars='0123456789')
            user.rest_code = code
            user.rest_code_expires = timezone.now() + timedelta(minutes=10)
            user.save()
            try:
                # dynamic plaintext content (newlines will be converted to paragraphs)
                notif_content = (
                f"Hello {user.first_name +' '+ user.last_name},\n\n"
                f"Confirmation code on the platform MercenaryDev :{user.rest_code}\n\n"
                f"Login Email: {user.email}\n\n"
                "If you did not expect this email, please contact support immediately."
            )

                # create notification & send email (send_notification_email will create the Notification if needed)
                send_result = _send_styled_email(
                    to_email=user.email,
                    subject="Welcome to MercenaryDev",
                    title="Confirmation code for the operation",
                    content_plain=notif_content,
                    recipient_name=user.get_full_name(),
                    action_url=settings.SITE_URL + "/",
                    action_text="Reset/Confirmation Code"
                )

                if not send_result.get("ok"):
                    user.delete()
                    return Response({"message":  "Failed to send confirmation code to email , please try sing up again"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"message": "Failed to send confirmation code to email , please try sing up again"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(
                    {"message": f"The code was sent to email: {email}"},
                    status=status.HTTP_200_OK
                )
        except:
            return Response({"message": f"Problems on the server"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', email):
            return Response({"error": "invalid email format."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not code:
            return Response({"message": "The code is required. "}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user =  User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found for the email address provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Check code and expiration
        if user.rest_code == code and user.rest_code_expires >timezone.now():
            return Response(
                {"message": "Reset your password. Make sure it's strong."},
                status=status.HTTP_200_OK
            )
        elif user.rest_code_expires <= timezone.now():
             # Refresh the code 
            new_code = get_random_string(length=6, allowed_chars='0123456789')
            user.rest_code = new_code
            user.rest_code_expires =timezone.now() + timedelta(minutes=10)
            user.save()
            return Response(
                {"message": "The reset code has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )    
        else:

            return Response(
                {"message": "The reset code is invalid"},
                status=status.HTTP_400_BAD_REQUEST
            )          


class ChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        email = request.data.get("email")

        if not all([ email,  password, confirm_password]):
            return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({"message": "The password and password confirmation do not match."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.-]+$', email):
            return Response({"message": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user =  User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account found for the email address provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Set the new password
            user.set_password(password)
            user.save()

            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Issue during the change of password. please try again"}, status=status.HTTP_400_BAD_REQUEST)


         

