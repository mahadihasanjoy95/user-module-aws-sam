import datetime
import json
import os

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from rds_data import execute_statement
from user_model import UserModel
from global_utils import get_response, dict_connection, get_formatted_validation_error
client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')

RegionName = os.getenv('RegionName')

logger = Logger(service="APP")


def lambda_handler(message, context):
    print(message)
    shouldCommit = False
    if ('body' not in message or
            message['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    payload = json.loads(message['body'])
    try:
        user_post = UserModel(**payload)
    except Exception as e:
        print("Exception to parse user data::::::::::  ", e)
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
    userType = user_post.userType
    email = user_post.email
    phone_number = user_post.phoneNumber
    created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    employeeId = "ABCDEFGHIJKLMN"
    isActive = True
    emailExists = check_email_exists(email)
    if emailExists:
        return {"statusCode": 400,
                'body': json.dumps({"message": "Email already exists in userpool"}),
                }

    insertSql = f"INSERT INTO user (name, mothersName, fathersName, dob, address, userType, email, employeeId, isActive, phoneNumber, createdAt) VALUES ('{name}', '{mothersName}','{fathersName}','{dob}','{address}','{userType}','{email}','{employeeId}', {isActive},'{phone_number}','{created_at}')"
    # response = {"records": {}}
    try:
        with dict_connection.cursor() as cursor:
            cursor.execute(insertSql)
            inserted_id = cursor.lastrowid
            user_post.id = inserted_id
        shouldCommit = True

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
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
    finally:
        if shouldCommit:
            dict_connection.commit()
        else:
            dict_connection.rollback()


def check_email_exists(email):
    try:
        response = client.admin_get_user(
            UserPoolId=UserPool,
            Username=email
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            return False
        else:
            raise e
