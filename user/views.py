import re

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from core.cognito_utils import get_jwt_cognito_id, refresh_jwt_token
from core.pagination import StandardResultsSetPagination
from user.models import Traveller, OTP, CognitoUser
from user.serializers import TravellerSerializer


class SendOTP(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        phone_number = request.data.get('mobile_number', '')
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')

        if not phone_pattern.match(phone_number):
            return Response({"success": False, "message": "Invalid Mobile Number"}, status=status.HTTP_400_BAD_REQUEST)

        if Traveller.objects.filter(mobile_number=phone_number).exists():
            return Response({"success": False, "message": "Mobile Number already registered. Please login"},
                            status=status.HTTP_400_BAD_REQUEST)
        session_id = request.data.get('session_id', '')
        if not session_id:
            return Response({"success": False, "message": "Invalid request. Session ID missing"},
                            status=status.HTTP_400_BAD_REQUEST)
        otp = OTP.send_otp(session_id, phone_number)
        return Response({"success": True, "OTP": otp, "message": "OTP has been sent successfully"})


class VerifyOTP(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        session_id = request.data.get('session_id', '')
        if not session_id:
            return Response({"success": False, "message": "Invalid request. Session ID missing"},
                            status=status.HTTP_400_BAD_REQUEST)
        otp = None
        try:
            otp = int(request.data.get('otp', None))
        except ValueError:
            pass
        if not otp:
            return Response({"success": False, "message": "OTP is missing"}, status=status.HTTP_400_BAD_REQUEST)
        success = OTP.verify_otp(session_id, otp)
        if success:
            return Response({'success': True, "message": "OTP verification successful"})
        else:
            return Response({'success': False, "message": "Invalid OTP. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class SendOTPLogin(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        phone_number = request.data.get('mobile_number', '')
        phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_pattern.match(phone_number):
            return Response({"success": False, "message": "Invalid Mobile Number"}, status=status.HTTP_400_BAD_REQUEST)
        if not Traveller.objects.filter(mobile_number=phone_number).exists():
            return Response({"success": False, "message": "Mobile Number not registered. Please Sign-Up"},
                            status=status.HTTP_400_BAD_REQUEST)
        session_id = request.data.get('session_id', '')
        if not session_id:
            return Response({"success": False, "message": "Invalid request. Session ID missing"},
                            status=status.HTTP_400_BAD_REQUEST)
        otp = OTP.send_otp(session_id, phone_number)
        return Response({"success": True, "OTP": otp, "message": "OTP has been sent successfully"})


class VerifyOTPLogin(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        session_id = request.data.get('session_id', '')
        if not session_id:
            return Response({"success": False, "message": "Invalid request. Session ID missing"},
                            status=status.HTTP_400_BAD_REQUEST)
        otp = None
        try:
            otp = int(request.data.get('otp', None))
        except ValueError:
            pass
        if not otp:
            return Response({"success": False, "message": "OTP is missing"}, status=status.HTTP_400_BAD_REQUEST)
        success = OTP.verify_otp(session_id, otp)
        mobile_number = request.data['mobile_number']
        if success:
            try:
                traveller = Traveller.objects.get(mobile_number=mobile_number)
                return Response({"success": True, "profile": traveller.get_profile(), "token": traveller.get_token(),
                                 "jwt_token": get_jwt_cognito_id(traveller.get_token(), traveller.user)})
            except Traveller.DoesNotExist:
                return Response({"success": False, "message": "Mobile Number not registered. Please Sign-Up"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, "message": "Invalid OTP. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class SignUpView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        mobile_number = request.data.get('mobile_number', '')
        email = request.data.get('email', '')
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        dob = request.data.get('dob', '')
        nationality = request.data.get('nationality', '')
        try:
            phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_pattern.match(mobile_number):
                return Response({"success": False, "message": "Mobile number is invalid"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Traveller.objects.filter(mobile_number=mobile_number).exists():
                return Response({"success": False, "message": "Mobile number already registered. Please login"},
                                status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=email).exists():
                return Response({"success": False, "message": "Email id is already in use"},
                                status=status.HTTP_400_BAD_REQUEST)
            traveller = Traveller.create_traveller_from_mobile_number(mobile_number, email, password, first_name,
                                                                      last_name,
                                                                      dob, nationality)
            return Response({"success": True, "profile": traveller.get_profile(), "token": traveller.get_token(),
                             "jwt_token": get_jwt_cognito_id(traveller.get_token(), traveller.user)
                             })
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        if "mobile_number" not in request.data or "password" not in request.data:
            message = "Mobile Number or Password Missing"
            return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)
        try:
            phone_number = request.data.get('mobile_number', '')
            password = request.data.get('password', '')
            phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
            if not phone_pattern.match(phone_number):
                return Response({"success": False, "message": "Invalid Mobile Number"},
                                status=status.HTTP_400_BAD_REQUEST)
            traveller = Traveller.objects.get(mobile_number=phone_number)
            if traveller.user.check_password(password):
                return Response({"success": True, "profile": traveller.get_profile(),
                                 "token": Token.objects.get(user=traveller.user).key,
                                 "jwt_token": get_jwt_cognito_id(traveller.get_token(), traveller.user)
                                 })
            else:
                message = "Password is incorrect"
        except Traveller.DoesNotExist:
            message = "Mobile Number not registered. Please sign up"
        return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        if "mobile_number" not in request.data:
            message = "Mobile Number Missing"
            return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)
        if not "password" in request.data:
            message = "Password Missing"
            return Response({"success": False, "message": message}, status=status.HTTP_400_BAD_REQUEST)
        try:
            mobile_number = request.data["mobile_number"]
            traveller = Traveller.objects.get(mobile_number=mobile_number)
            user = traveller.user
            user.set_password(request.data['password'])
            user.save()
            return Response({"success": True, "message": "Password has been set successfully"})
        except Traveller.DoesNotExist:
            return Response({"success": False, "message": "Mobile Number not registered. Please sign up"},
                            status=status.HTTP_400_BAD_REQUEST)


class SocialLoginView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        traveller = None
        email = request.data.get('email', '')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        if not email:
            return Response({"success": False, "message": "An error occurred. Please try login using Google"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            if User.objects.filter(username=email).exists():
                traveller = Traveller.objects.get(user__email=email)
            if not traveller:
                traveller = Traveller.create_traveller_from_email(email, first_name, last_name)
                if 'profile_picture' in request.data:
                    profile_picture = request.data['profile_picture']
                    traveller.profile_picture = profile_picture
                    traveller.save()
            return Response({"success": True, "profile": traveller.get_profile(),
                             "token": traveller.get_token(),
                             "jwt_token": get_jwt_cognito_id(traveller.get_token(), traveller.user)
                             })
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):

    def put(self, request):
        try:
            traveller = Traveller.objects.get(user=request.user)
            mobile_number = request.data.get('mobile_number', '')
            if Traveller.objects.filter(mobile_number=mobile_number).exclude(id=traveller.id).exists():
                return Response({"success": False, "message": "Mobile number is already in use"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                traveller.update_profile(request.data)
                return Response({"success": True, "profile": traveller.get_profile(), "token": traveller.get_token()})
        except:
            return Response({"success": False, "message": "Profile not updated.", "profile": traveller.get_profile(),
                             "token": traveller.get_token()})

    def get(self, request):
        try:
            traveller = Traveller.objects.get(user=request.user)
            return Response({"success": True, "profile": traveller.get_profile(), "token": traveller.get_token()})
        except:
            return Response({"success": False, "profile": traveller.get_profile(), "token": traveller.get_token()})


class ProfilePictureView(APIView):

    def put(self, request):
        try:
            traveller = Traveller.objects.get(user=request.user)
            profile_picture = None
            if 'profile_picture' in request.data:
                profile_picture = request.data['profile_picture']
            traveller.profile_picture = profile_picture
            traveller.save()
            return Response({"success": True, "message": "Profile picture updated successfully",
                             "profile_picture": traveller.get_profile_picture()})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class BanUser(APIView):

    def post(self, request):
        banned_user = Traveller.objects.get(pk=request.data['id'])
        ban_reason = request.data['reason']
        banned_user.is_banned = True
        banned_user.ban_reason = ban_reason
        banned_user.save()
        return Response({"success": True, "message": "The Requested Yatra User has been Banned."})


class LiftBan(APIView):

    def post(self, request):
        yatra_user = Traveller.objects.get(pk=request.data['id'])
        if yatra_user.is_banned:
            yatra_user.is_banned = False
            yatra_user.save()
        return Response({"success": True, "message": "The Ban has been lifted from requested Yatra User."})


class UsersView(generics.ListAPIView):
    serializer_class = TravellerSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Traveller.objects.all().order_by('created_on')


class LastLoginView(APIView):

    def get(self, request):
        try:
            user = request.user
            last_login = user.last_login
            user.last_login = timezone.now()
            user.save()
            return Response({"success": True, "last_login": last_login})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):

    def get(self, request):
        try:
            user = request.user
            cognito_user = CognitoUser.objects.get(user=user)
            jwt_token = refresh_jwt_token(cognito_user)
            return Response({"success": True, "jwt_token": jwt_token})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)
