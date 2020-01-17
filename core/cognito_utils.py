import boto3
from boto3.dynamodb.conditions import Key
from django.conf import settings

from user.models import CognitoUser

client = boto3.client('cognito-idp', region_name=settings.AWS_USER_POOL_REGION)
dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_USER_POOL_REGION)


def get_jwt_cognito_id(token, user):
    id = str(user.id)
    try:
        try:
            client.admin_get_user(UserPoolId=settings.AWS_USER_POOL_ID, Username=token)
        except:
            custom_email = id + '@test.com'
            client.sign_up(ClientId=settings.AWS_USER_POOL_CLIENT_ID, Username=token, Password=token,
                           UserAttributes=[{'Name': 'email', 'Value': custom_email}, ])
            client.admin_confirm_sign_up(UserPoolId=settings.AWS_USER_POOL_ID, Username=token)

        user_table = dynamodb.Table(settings.AWS_DYNAMO_USER_TABLE)
        user_list = user_table.query(KeyConditionExpression=Key('id').eq(id))
        if user_list['Count'] == 0:
            user_table.put_item(Item={'id': id, 'displayName': user.get_full_name(),
                                      'userName': user.username,
                                      'isPremium': False})
        response = client.admin_initiate_auth(UserPoolId=settings.AWS_USER_POOL_ID,
                                              ClientId=settings.AWS_USER_POOL_CLIENT_ID,
                                              AuthFlow='ADMIN_NO_SRP_AUTH',
                                              AuthParameters={'USERNAME': token, 'PASSWORD': token})
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']
        if CognitoUser.objects.filter(user=user).exists():
            cognito_user = CognitoUser.objects.get(user=user)
            cognito_user.id_token = id_token
            cognito_user.access_token = access_token
            cognito_user.refresh_token = refresh_token
            cognito_user.save()
        else:
            CognitoUser.objects.create(user=user, id_token=id_token, access_token=access_token,
                                       refresh_token=refresh_token)
        return id_token
    except:
        return {}


def update_member_cognito(id, full_name):
    try:
        user_table = dynamodb.Table(settings.AWS_DYNAMO_USER_TABLE)
        user_table.update_item(Key={'id': id},
                               UpdateExpression="set displayName = :r, userName = :p",
                               ExpressionAttributeValues={':r': full_name, ':p': full_name},
                               ReturnValues="UPDATED_NEW")
    except:
        pass
    return None


def refresh_jwt_token(cognito_user):
    response = client.admin_initiate_auth(UserPoolId=settings.AWS_USER_POOL_ID,
                                          ClientId=settings.AWS_USER_POOL_CLIENT_ID,
                                          AuthFlow='REFRESH_TOKEN_AUTH',
                                          AuthParameters={'REFRESH_TOKEN': cognito_user.refresh_token})
    id_token = response['AuthenticationResult']['IdToken']
    access_token = response['AuthenticationResult']['AccessToken']
    cognito_user.id_token = id_token
    cognito_user.access_token = access_token
    cognito_user.save()
    return id_token
