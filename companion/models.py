from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from companion.thread import CompanionNotificationThread
from user.models import Traveller

REQUEST_STATUS_CHOICES = (('ACTIVE', 'ACTIVE'), ('ACCEPTED', 'ACCEPTED'), ('COMPLETED', 'COMPLETED'),
                          ('REJECTED', 'REJECTED'))

COMPANION_REQUEST_CHOICES = (('INTERESTED', 'INTERESTED'), ('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'))


class Request(models.Model):
    TRIP_TYPE_CHOICES = (('one-way', 'one-way'), ('round', 'round'))
    TRAVELER_TYPE_CHOICES = (
        ('self', 'self'), ('parents', 'parents'), ('spouse', 'spouse'), ('kids', 'kids'), ('other', 'other'))
    SPONSORSHIP_CHOICES = (
        ('none', 'none'), ('one-third', 'one-third'), ('half', 'half'), ('full', 'full'), ('other', 'other'))

    request_owner = models.ForeignKey(Traveller, on_delete=models.CASCADE)
    trip_type = models.CharField(choices=TRIP_TYPE_CHOICES, max_length=7)
    origin_airport = models.CharField(max_length=250)
    destination_airport = models.CharField(max_length=250)
    departure_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    departure_airlines = models.CharField(max_length=30)
    return_airlines = models.CharField(max_length=30, blank=True, null=True)
    adults = models.IntegerField(default=0)
    traveler_type = models.CharField(choices=TRAVELER_TYPE_CHOICES, max_length=15)
    sponsorship = models.CharField(choices=SPONSORSHIP_CHOICES, max_length=15)
    sponsorship_desc = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=REQUEST_STATUS_CHOICES, default='ACTIVE', max_length=10)

    def __str__(self):
        return self.request_owner.get_full_name()

    def get_request_details(self):
        return {'owner': self.request_owner.get_full_name(), 'trip_type': self.trip_type,
                'origin_airport': self.origin_airport, 'destination_airport': self.destination_airport,
                'departure_date': self.departure_date, 'return_date': self.return_date,
                'departure_airlines': self.departure_airlines, 'return_airlines': self.return_airlines,
                'adults': self.adults,
                'traveler_type': self.traveler_type, 'sponsorship': self.sponsorship,
                'sponsorship_desc': self.sponsorship_desc, 'created_on': self.created_on}

    def get_companions(self):
        companion_qs = Companion.objects.filter(request=self).order_by('status')
        data = []
        for qs in companion_qs:
            data.append(
                {'companion_id': qs.id, 'id': qs.requestor.user.id,
                 'name': qs.requestor.get_full_name(),
                 'image': qs.requestor.get_profile_picture(),
                 'nationality': qs.requestor.nationality,
                 'age': qs.requestor.get_age(), 'created_on': qs.created_on,
                 'message': qs.message, 'status': qs.status, 'verified': qs.requestor.verified})
        return data


class Companion(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    requestor = models.ForeignKey(Traveller, on_delete=models.CASCADE)
    message = models.CharField(max_length=400)
    status = models.CharField(choices=COMPANION_REQUEST_CHOICES, default='INTERESTED', max_length=10)
    created_on = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    traveller = models.ForeignKey(Traveller, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    headline = models.CharField(max_length=250)
    review = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Traveller: {} Request: {}".format(self.traveller, self.request)


@receiver(post_save, sender=Companion)
def send_notification(sender, instance=None, created=False, **kwargs):
    if not instance.status == 'REJECTED':
        CompanionNotificationThread(instance).start()
