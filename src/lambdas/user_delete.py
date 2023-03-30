import json
import os
from random import randint

import boto3
from aws_lambda_powertools import Logger
from pydantic import BaseModel, validator, constr, EmailStr
from rds_data import execute_statement
from user_model import UserEditModel

client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')
logger = Logger(service="APP")


def lambda_handler(message, context):
    if ('body' not in message or
            message['httpMethod'] != 'GET'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    userId = message['pathParameters']['id']

    fetchSql = f"SELECT email FROM user WHERE id = {userId}"
    try:
        response = execute_statement(fetchSql)
        email = response['records'][0][0]['stringValue']
        print("Target email:::: ", email)
        client.admin_delete_user(
            UserPoolId=UserPool,
            Username=email
        )
        print("User deleted from cognito successfully!!")

    except Exception as e:
        print("Exception to insert in api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
    deleteFromDependentTable = f"DELETE FROM user_role WHERE userId = {userId};"
    try:
        execute_statement(deleteFromDependentTable)
    except Exception as e:
        print("Exception to delete from user_role table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't delete the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
    deleteSql = f"DELETE FROM user WHERE id = {userId};"

    try:
        execute_statement(deleteSql)
        return {
            "statusCode": 200,
            "headers": {},
            'body': json.dumps({"message": "User Deleted Successfully!"}, indent=4, sort_keys=True, default=str),
            # efault=decimal_default),
        }
    except Exception as e:
        print("Exception to delete in user table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't delete the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
