from datetime import datetime

import pytz
from django.conf import settings
from fcm_django.models import FCMDevice
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.cron import inactivity_notification_job
from core.cron import expired_notification_job


class RegisterView(APIView):

    def post(self, request):
        registration_id = request.data.get('registration_id')
        if not registration_id:
            return Response({"success": False, "message": "Registration id not provided"},
                            status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        try:
            fcm_device = FCMDevice.objects.get(user=user)
            fcm_device.registration_id = registration_id
            fcm_device.date_created = datetime.now(pytz.utc)
            fcm_device.save()
            return Response({"success": True})
        except FCMDevice.DoesNotExist:
            FCMDevice.objects.create(user=user, registration_id=registration_id, type='web',
                                     date_created=datetime.now(pytz.utc))
            return Response({"success": True})
        except:
            return Response({"success": False})


class InactivityView(APIView):

    def get(self, request):
        inactivity_notification_job()
        return Response({"success": True})


class MessageView(APIView):

    def post(self, request):
        try:
            user = request.user
            user_id = request.data.get('user_id')
            message = request.data.get('message')
            request_id = request.data.get('request_id')
            fcm_device = FCMDevice.objects.get(user__id=user_id)
            title = "Message from {}".format(user.first_name)
            click_action = settings.YATRA_PORTAL + '#/companion-chat/{}/{}/{}'.format(
                str(request_id), str(user_id), str(user.id))
            fcm_device.send_message(title=title,
                                    body=message,
                                    icon="https://qa-api.yatraninja.com/static/images/logo.png",
                                    click_action=click_action
                                    )
            return Response({"success": True})
        except:
            return Response({"success": False, "message": "An error occurred. Please try again"},
                            status=status.HTTP_400_BAD_REQUEST)
