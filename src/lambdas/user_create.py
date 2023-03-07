import json
import os
import uuid
from datetime import datetime

import boto3

client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')


def lambda_handler(message, context):
    if ('body' not in message or
            message['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    table_name = os.environ.get('TABLE', 'pwsp_revenue_system')
    region = os.environ.get('REGION', 'ap-northeast-1')
    item_table = boto3.resource(
        'dynamodb',
        region_name=region
    )

    table = item_table.Table(table_name)
    user = json.loads(message['body'])
    randomString = str(uuid.uuid4())
    params = {
        'PK': "USER#",
        'SK': "USER#" + randomString,
        'firstName': user['firstName'],
        'lastName': user['lastName'],
        'isActive': user['isActive'],
        'email': user['email'],
        'phoneNumber': user['phoneNumber'],
        'createdAt': str(datetime.timestamp(datetime.now())),
        "GSI1PK": "USER#" + randomString,
        "GSI1SK": "USER#"
    }
    table.put_item(
        TableName=table_name,
        Item=params
    )

    """
    Create user forcefully confirm the user mail also and generate random password.
    """
    response = client.admin_create_user(
        UserPoolId=UserPool,
        Username=user['email'],
        MessageAction='SUPPRESS',
    )

    """
    Set the actual password to the user
    """
    client.admin_set_user_password(
        UserPoolId=UserPool,
        Username=user['email'],
        Password=user['password'],
        Permanent=True
    )
    """
    Assign role to user
    """
    client.admin_add_user_to_group(UserPoolId=UserPool, Username=user['email'], GroupName=user['role'])

    return {
        "statusCode": 200,
        "headers": {},
        'body': json.dumps(response, indent=4, sort_keys=True, default=str),  # default=decimal_default),
    }
