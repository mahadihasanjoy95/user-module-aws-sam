import datetime
import json
import os

import boto3
from aws_lambda_powertools import Logger
from user_model import UserEditModel

client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')
RegionName = os.getenv('RegionName')

logger = Logger(service="APP")
from global_utils import get_response, dict_connection


def lambda_handler(message, context):
    shouldCommit = False
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
    mothers_name = user_post.mothersName
    fathers_name = user_post.fathersName
    dob = user_post.dob
    address = user_post.address
    updated_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_type = user_post.userType
    user_id = user_post.id

    editSql = f"UPDATE user SET name = '{name}', mothersName ='{mothers_name}' , fathersName = '{fathers_name}', dob = '{dob}', address = '{address}', updatedAt = '{updated_at}', userType = '{user_type}'  WHERE id  = {user_id};"
    # response = {"records": {}}
    try:
        with dict_connection.cursor() as cursor:
            cursor.execute(editSql)
            inserted_id = cursor.lastrowid
            user_post.id = inserted_id
        shouldCommit = True
        return get_response(
            status=200,
            error=False,
            message="News Created Successfully",
            data=user_post.dict()
        )
    except Exception as e:
        shouldCommit = True
        print("Exception to insert in api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't update the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
    finally:
        if shouldCommit:
            dict_connection.commit()
        else:
            dict_connection.rollback()
