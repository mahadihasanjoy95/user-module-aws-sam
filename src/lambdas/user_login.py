import boto3
import os
import json

client = boto3.client('cognito-idp')

UserPoolClient = os.getenv('UserPoolClient')


def lambda_handler(message, context):
    if ('body' not in message or
            message['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    user = json.loads(message['body'])

    """
    This initiate auth method from boto3 client will match the mail and pass from user pool and return all the token
    """
    auth_response = client.initiate_auth(
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': user['email'],
            'PASSWORD': user['password']
        },
        ClientId=UserPoolClient
    )

    return {
        "statusCode": 200,
        "headers": {},
        'body': json.dumps(auth_response, indent=4, sort_keys=True, default=str),  # default=decimal_default),
    }
