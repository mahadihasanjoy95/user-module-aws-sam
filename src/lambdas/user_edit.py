import datetime
import json
import os

import boto3
from aws_lambda_powertools import Logger
from rds_data import execute_statement
from user_model import UserEditModel

client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')

DynamoTableName = os.getenv('DynamoTableName')
RegionName = os.getenv('RegionName')

logger = Logger(service="APP")


def lambda_handler(message, context):
    if ('body' not in message or
            message['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    """
    Insert Aurora MySQL part
    """
    payload = json.loads(message['body'])
    try:
        user_post = UserEditModel(**payload)
    except Exception as e:
        print("Exception to create user table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": str(e)}),
                # "location": ip.text.replace("\n", "")

                }
    # Extract values from the payload
    name = user_post.name
    mothersName = user_post.mothersName
    fathersName = user_post.fathersName
    dob = user_post.dob
    address = user_post.address
    updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    userType = user_post.userType
    userId = user_post.id
    parameters = [
        {'name': 'name', 'value': {'stringValue': name}},
        {'name': 'mothersName', 'value': {'stringValue': mothersName}},
        {'name': 'fathersName', 'value': {'stringValue': fathersName}},
        {'name': 'dob', 'value': {'stringValue': dob}},
        {'name': 'address', 'value': {'stringValue': address}},
        {'name': 'userType', 'value': {'stringValue': userType}},
        {'name': 'userId', 'value': {'longValue': userId}},
        {'name': 'updatedAt', 'value': {'stringValue': updated_at}}
    ]

    editSql = f"UPDATE user SET name = :name, mothersName = :mothersName, fathersName = :fathersName, dob = :dob, address = :address, updatedAt = :updatedAt, userType = :userType  WHERE id  = :userId;"
    # response = {"records": {}}
    try:
        execute_statement(editSql, parameters)
        return {
            "statusCode": 200,
            "headers": {},
            'body': json.dumps({"message": "Successfully Updated!"}, indent=4, sort_keys=True, default=str),
            # default=decimal_default),
        }
    except Exception as e:
        print("Exception to insert in api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
