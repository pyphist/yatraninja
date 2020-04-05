from core.settings.base import *

AWS_ACCESS_KEY_ID = 'AKIATSUXKKUX3J6VOAAR'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

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

AWS_USER_POOL_ID = 'ap-south-1_0Pqyub9Xa'
AWS_USER_POOL_REGION = 'ap-south-1'
AWS_USER_POOL_CLIENT_ID = '6f3j6afs8i17fog9la5sdvfrgb'
AWS_DYNAMO_USER_TABLE = 'User-ap57eokcj5gjvmony6syzfi5cm-dev'

# DATABASES = {
#     'default': {
#         "ENGINE": 'django.db.backends.mysql',
#         'NAME': 'qa_yatra_ninja',
#         'USER': 'yninja',
#         'PASSWORD': 'i5aPuUNcA4iTs',
#         'PORT': '3306',
#         'HOST': '13.234.126.120'
#     }
# }

FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": "AAAAiOKBX9o:APA91bG3DFkf-r-ecaXVHNd6eOSCnUok8w16RNWplsMS0HAcENrQxqedZ56dZej2ZM5rrfxA2eOXer-ACV74GRwvuQMbJSHM6R_zIW7QG8reTU7rUBdP99Jh0PFrRC4sFT7UIWrC0zqD"
}

YATRA_PORTAL = "https://qa-portal.yatraninja.com/"
