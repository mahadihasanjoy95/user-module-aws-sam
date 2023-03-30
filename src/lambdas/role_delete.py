import json
import os

import boto3
from aws_lambda_powertools import Logger
from rds_data import execute_statement

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
    name = message['pathParameters']['name']

    deleteFromDependentTable = f"DELETE FROM user_role WHERE roleName = '{name}';"
    try:
        execute_statement(deleteFromDependentTable)
    except Exception as e:
        print("Exception to delete from user_role table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't delete the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
    deleteFromDependentTable = f"DELETE FROM role_api WHERE roleName = '{name}';"
    try:
        execute_statement(deleteFromDependentTable)
    except Exception as e:
        print("Exception to delete from role_api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't delete the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
    deleteSql = f"DELETE FROM role WHERE roleName = '{name}';"

    try:
        execute_statement(deleteSql)
        return {
            "statusCode": 200,
            "headers": {},
            'body': json.dumps({"message": "Role Deleted Successfully!"}, indent=4, sort_keys=True, default=str),
            # efault=decimal_default),
        }
    except Exception as e:
        print("Exception to delete in Role table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't delete the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
