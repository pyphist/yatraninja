import threading

from django.conf import settings
from django.template.loader import get_template
from fcm_django.models import FCMDevice

from core.utils import generate_html_from_json, send_email


class NewCompanionRequestThread(threading.Thread):

    def __init__(self, request, **kwargs):
        self.request = request
        super(NewCompanionRequestThread, self).__init__(**kwargs)

    def run(self):
        try:
            request = self.request
            # Send New Request Information
            subject = "Yatra Ninja : New Request " + str(request.id) + " Posted"
            mail_content = generate_html_from_json(request.get_request_details())
            request_context = {}
            request_context['mail_content'] = mail_content
            message = get_template('request.html').render(request_context)
            send_email(subject, None, message)
        except:
            pass


class CompanionNotificationThread(threading.Thread):

    def __init__(self, companion, **kwargs):
        self.companion = companion
        super(CompanionNotificationThread, self).__init__(**kwargs)

    def run(self):
        try:
            portal = settings.YATRA_PORTAL
            status = self.companion.status
            owner = self.companion.request.request_owner.user
            companion = self.companion.requestor.user
            if status == 'INTERESTED':
                title = "Hey {}!".format(owner.first_name)
                body = 'You have received a trip interest from {}. Click to view interest'.format(companion.first_name)
                click_action = portal + '#/trip-requests/' + str(self.companion.request.id)
                fcm_device = FCMDevice.objects.get(user=owner)
            elif status == 'ACCEPTED':
                title = "Hey {}!".format(companion.first_name)
                body = 'Your trip interest has been accepted. Click to start chatting'
                click_action = portal + '#/companion-chat/{}/{}/{}'.format(
                    str(self.companion.request.id), str(companion.id), str(owner.id))
                fcm_device = FCMDevice.objects.get(user=companion)
            fcm_device.send_message(title=title,
                                    body=body,
                                    icon="https://qa-api.yatraninja.com/static/images/logo.png",
                                    click_action=click_action)
        except:
            pass
