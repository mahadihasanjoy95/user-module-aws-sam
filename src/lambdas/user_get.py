import boto3
import os
import json
from boto3.dynamodb.conditions import Key

DynamoTableName = os.getenv('DynamoTableName')
RegionName = os.getenv('RegionName')


def lambda_handler(message, context):
    if ('httpMethod' not in message or
            message['httpMethod'] != 'GET'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }

    table_name = DynamoTableName
    region = RegionName

    item_table = boto3.resource(
        'dynamodb',
        region_name=region
    )

    table = item_table.Table(table_name)
    """
    Query to get all the users from the table
    """
    response = table.query(
        KeyConditionExpression=Key('PK').eq('USER#')
    )

    return {
        "statusCode": 200,
        "headers": {},
        'body': json.dumps(response['Items'], indent=4, sort_keys=True, default=str),  # default=decimal_default),
    }
