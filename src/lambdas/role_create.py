import json
import os

import boto3

client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')


def lambda_handler(message, context):
    """
    This part will just check that the request is post method
    TODO: there should be validation with powertool and pydantic
    """
    if ('body' not in message or
            message['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    """
    TODO: This database part should be optimized & have to Check that role exists in DB or not
    """
    table_name = os.environ.get('TABLE', 'pwsp_revenue_system')
    region = os.environ.get('REGION', 'ap-northeast-1')
    item_table = boto3.resource(
        'dynamodb',
        region_name=region
    )

    table = item_table.Table(table_name)
    payload = json.loads(message['body'])

    params = {
        'PK': "ROLE#",
        'SK': payload['roleName'] + "#",
        'role_desc': payload['roleDesc']
    }
    table.put_item(
        TableName=table_name,
        Item=params
    )
    """
    Create group into user-pool. Here group is actually define the role
    """
    reply = client.create_group(UserPoolId=UserPool, GroupName=payload['roleName'])
    return {
        "statusCode": 200,
        "headers": {},
        'body': json.dumps(reply, indent=4, sort_keys=True, default=str),  # default=decimal_default),
    }
