from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class ProfilePicStorage(S3Boto3Storage):
    location = settings.AWS_PROFILE_LOCATION
    file_overwrite = False
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN