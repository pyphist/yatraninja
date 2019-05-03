import os

import boto3
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.timezone import now
from json2html import json2html


def upload_media_to(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    return '%s%s' % (now().strftime("%Y%m%d%H%M%S"), filename_ext.lower(),)


def send_sms_sns(to, message):
    # Create an SNS client
    client = boto3.client("sns", aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name='ap-southeast-1')

    # Send your sms message.
    return client.publish(PhoneNumber=to, Message=message)


def send_sms(to, message):
    return send_sms_sns(to, message)


def send_email(subject, receiver, mail_content, headers=None):
    try:
        if receiver is None:
            receiver = settings.EMAIL_TO
        mail = EmailMessage(subject, mail_content, settings.DEFAULT_FROM_EMAIL, [receiver], headers=headers)
        mail.content_subtype = 'html'
        mail.send()
    except:
        pass


def generate_html_from_json(data):
    html_data = json2html.convert(json=data)
    return html_data
