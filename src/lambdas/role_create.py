import json
import os

import boto3
from rds_data import execute_statement

UserPool = os.getenv('UserPool')

client = boto3.client('cognito-idp')


def lambda_handler(event, context):
    payload = json.loads(event['body'])

    # Extract values from the payload
    roleName = payload['roleName']
    roleDescription = payload['roleDescription']

    insertSql = f"INSERT INTO role (roleName, roleDescription) VALUES ('{roleName}', '{roleDescription}')"
    try:
        execute_statement(insertSql)
        """
        #     Create group into user-pool. Here group is actually define the role
        #     """
        reply = client.create_group(UserPoolId=UserPool, GroupName=roleName)

        return {"statusCode": 200,
                'body': json.dumps({"message": "Successfully Inserted"}),
                # "location": ip.text.replace("\n", "")

                }

    except Exception as e:
        print("Exception to insert in role table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
