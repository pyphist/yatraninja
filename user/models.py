import datetime

from random import randint
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from core.storage import ProfilePicStorage
from core.utils import upload_media_to, send_sms

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Mobile Number must be entered in the format: "
                                                               "'+XXXXXXXX'. Up to 15 digits allowed.")


class Traveller(models.Model):
    GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(validators=[phone_regex], max_length=17, unique=True, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    nationality = models.CharField(max_length=250, blank=True, null=True)
    profile_picture = models.ImageField(storage=ProfilePicStorage(), upload_to=upload_media_to, blank=True, null=True)
    is_banned = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    ban_reason = models.CharField(max_length=300, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_first_name(self):
        return self.user.first_name

    get_first_name.short_description = "First Name"

    def get_last_name(self):
        return self.user.last_name

    get_last_name.short_description = "Last Name"

    def get_full_name(self):
        return "{} {}".format(self.get_first_name(), self.get_last_name())

    def get_token(self):
        return Token.objects.get(user=self.user).key

    def get_profile_picture(self):
        if not self.profile_picture or self.profile_picture.name == 'null':
            return None
        else:
            return self.profile_picture.url

    @classmethod
    def create_traveller_from_mobile_number(cls, mobile_number, email, password, first_name, last_name, dob,
                                            nationality):
        if User.objects.filter(username=email).exists():
            user = User.objects.get(username=email)
        else:
            user = User.objects.create(username=email, first_name=first_name, last_name=last_name, email=email)
            if not password:
                password = User.objects.make_random_password()
                try:
                    message = "Your Yatra Ninja Login Password is " + str(password)
                    send_sms(mobile_number, message)
                except:
                    pass
            user.set_password(password)
            user.save()
        dob_obj = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        yatra_user = cls.objects.create(user=user, mobile_number=mobile_number, dob=dob_obj, nationality=nationality)
        return yatra_user

    @classmethod
    def create_traveller_from_email(cls, email, first_name, last_name):
        user = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        yatra_user = cls.objects.create(user=user, verified=True)
        return yatra_user

    def get_profile(self):
        return {'id': self.id, 'user_id': self.user.id, 'mobile_number': self.mobile_number,
                'first_name': self.get_first_name(), 'last_name': self.get_last_name(), 'email': self.user.email,
                'gender': self.gender, 'address': self.address, 'dob': self.dob,
                'nationality': self.nationality, 'age': self.get_age(), 'verified': self.verified,
                'profile_picture': self.get_profile_picture(), 'last_login': self.user.last_login}

    def update_profile(self, data):
        if 'first_name' in data:
            first_name = data['first_name']
            if first_name:
                self.user.first_name = first_name
        if 'last_name' in data:
            last_name = data['last_name']
            if last_name:
                self.user.last_name = last_name
        if 'password' in data:
            password = data['password']
            if password:
                self.user.set_password(password)
        if 'mobile_number' in data:
            mobile_number = data['mobile_number']
            if mobile_number:
                self.mobile_number = mobile_number
        if 'gender' in data:
            gender = data['gender']
            if gender:
                self.gender = gender
        if 'nationality' in data:
            nationality = data['nationality']
            if nationality:
                self.nationality = nationality
        if 'dob' in data:
            dob_str = data.get('dob', '')
            if dob_str:
                dob_obj = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
                self.dob = dob_obj
        if 'address' in data:
            address = data['address']
            if address:
                self.address = address
        self.user.save()
        self.save()

    def get_age(self):
        if not self.dob:
            return 0
        today = datetime.date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def random_number(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


class OTP(models.Model):
    OTP_LENGTH = 6
    session_id = models.CharField(max_length=100)
    otp = models.IntegerField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    @classmethod
    def generate_otp(cls, session_id):
        yatra_user_otp = cls.objects.get_or_create(session_id=session_id)[0]
        otp = random_number(OTP.OTP_LENGTH)
        yatra_user_otp.otp = otp
        yatra_user_otp.save()
        return otp

    @classmethod
    def get_otp_message(cls, otp):
        message = "{} is the One Time Password(OTP) for your Yatra Ninja Mobile Verification.".format(otp)
        return message

    @classmethod
    def send_otp(cls, session_id, mobile_number):
        otp = cls.generate_otp(session_id)
        message = OTP.get_otp_message(otp)
        send_sms(mobile_number, message)
        return otp

    @classmethod
    def verify_otp(cls, session_id, otp):
        try:
            yatra_user_otp = cls.objects.get(session_id=session_id)
            return yatra_user_otp.otp == otp
        except cls.DoesNotExist:
            return False


class CognitoUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_token = models.CharField(max_length=2500)
    access_token = models.CharField(max_length=2500)
    refresh_token = models.CharField(max_length=2500)

    def __str__(self):
        return self.user.username
