from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.db.models import Q
from fcm_django.models import FCMDevice

from companion.models import Request


def inactivity_notification_job():
    last_active_date = datetime.now(pytz.utc) - timedelta(days=1)
    query_set = FCMDevice.objects.filter(date_created__lt=last_active_date).values('id')
    for data in query_set:
        device_id = data['id']
        device = FCMDevice.objects.get(pk=device_id)
        first_name = device.user.first_name
        title = "There"
        if first_name:
            title = first_name
        title = "Hey {}!".format(title)
        click_action = settings.YATRA_PORTAL
        device.send_message(title=title,
                            body="It's been so long since you have visited Yatra Ninja Portal. Click to open portal",
                            icon="https://qa-api.yatraninja.com/static/images/logo.png",
                            click_action=click_action
                            )


def expired_notification_job():
    try:
        current_date = datetime.now(pytz.utc)
        query_set = Request.objects.filter(Q(departure_date__lt=current_date) & Q(trip_type='one-way') | Q(trip_type='round') & Q(
                return_date__lt=current_date))
        for data in query_set:
            data.status = "COMPLETED"
            data.save()
    except:
        pass
