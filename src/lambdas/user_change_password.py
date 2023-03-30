import json
import os

import boto3
from botocore.exceptions import ClientError

client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')


def lambda_handler(event, context):
    if ('body' not in event or
            event['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    payload = json.loads(event['body'])
    try:
        response = client.admin_set_user_password(
            UserPoolId=UserPool,
            Username=payload['email'],
            Password=payload['password'],
            Permanent=True
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Password changed successfully')
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(e.response['Error']['Message'])
        }
