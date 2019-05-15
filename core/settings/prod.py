from core.settings.base import *

AWS_ACCESS_KEY_ID = 'AKIAJZFWLE3EQYSJV5RA'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = "us-east-1"

DATABASES = {
    'default': {
        "ENGINE": 'django.db.backends.mysql',
        'NAME': 'yatra_ninja',
        'USER': 'yatra_ninja',
        'PASSWORD': 'yatra_ninja',
        'PORT': '3306',
        'HOST': 'localhost'
    }

}

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'qa-api.yatraninja.com']

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": "AAAAiOKBX9o:APA91bG3DFkf-r-ecaXVHNd6eOSCnUok8w16RNWplsMS0HAcENrQxqedZ56dZej2ZM5rrfxA2eOXer-ACV74GRwvuQMbJSHM6R_zIW7QG8reTU7rUBdP99Jh0PFrRC4sFT7UIWrC0zqD"
}

YATRA_PORTAL = "https://portal.yatraninja.com/"
