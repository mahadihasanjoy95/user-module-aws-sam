import json
import os
from random import randint
from rds_data import execute_statement

import boto3
from datetime import datetime
from http import HTTPStatus
from typing import Optional, Any, Dict, List

import pydantic
from pydantic import BaseModel, Field, validator

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths

client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')

DynamoTableName = os.getenv('DynamoTableName')
RegionName = os.getenv('RegionName')

logger = Logger(service="APP")


class UserModel(BaseModel):
    userName: str = Field(..., max_length=10)
    firstName: str
    lastName: str
    email: str
    password: str

    @validator('userName', each_item=True)
    def check_names_not_empty(cls, v):
        assert v != '', 'Empty strings are not allowed.'
        return v


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
    createSql = "CREATE TABLE  IF NOT EXISTS user ( id int NOT NULL, firstName varchar(255) NOT NULL, lastName varchar(255) NOT NULL, userName varchar(255) NOT NULL, email varchar(255) NOT NULL, PRIMARY KEY (id));"
    try:
        response = execute_statement(createSql)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create user table::::::::::  ", e)
    payload = json.loads(message['body'])
    try:
        user_post = UserModel(**payload)
    except Exception as e:
        print("Exception to create user table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Bad Request!!"}),
                # "location": ip.text.replace("\n", "")

                }
    # Extract values from the payload
    firstName = user_post.firstName
    lastName = user_post.lastName
    userName = user_post.userName
    email = user_post.email
    randomId = randint(1, 1000)

    insertSql = f"INSERT INTO user (id,firstName, lastName, userName,email) VALUES ({randomId},'{firstName}', '{lastName}','{userName}','{email}')"
    # response = {"records": {}}
    try:
        execute_statement(insertSql)
        """
           Create user forcefully confirm the user mail also and generate random password.
        """
        response = client.admin_create_user(
            UserPoolId=UserPool,
            Username=user_post.email,
            MessageAction='SUPPRESS',
        )

        """
        Set the actual password to the user
        """
        client.admin_set_user_password(
            UserPoolId=UserPool,
            Username=user_post.email,
            Password=user_post.password,
            Permanent=True
        )

        return {
            "statusCode": 200,
            "headers": {},
            'body': json.dumps(response, indent=4, sort_keys=True, default=str),  # default=decimal_default),
        }
    except Exception as e:
        print("Exception to insert in api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }

    """
    Inseert DynamoDB part
    """
    # table_name = DynamoTableName
    # region = RegionName
    # item_table = boto3.resource(
    #     'dynamodb',
    #     region_name=region
    # )
    #
    # table = item_table.Table(table_name)
    # user = json.loads(message['body'])
    # randomString = str(uuid.uuid4())
    # params = {
    #     'PK': "USER#",
    #     'SK': "USER#" + randomString,
    #     'firstName': user['firstName'],
    #     'lastName': user['lastName'],
    #     'isActive': user['isActive'],
    #     'email': user['email'],
    #     'phoneNumber': user['phoneNumber'],
    #     'createdAt': str(datetime.timestamp(datetime.now())),
    #     "GSI1PK": "USER#" + randomString,
    #     "GSI1SK": "USER#"
    # }
    # table.put_item(
    #     TableName=table_name,
    #     Item=params
    # )
