import json
import os
import uuid
from datetime import datetime

import boto3
from random import randint
client = boto3.client('cognito-idp')

UserPool = os.getenv('UserPool')

DynamoTableName = os.getenv('DynamoTableName')
RegionName = os.getenv('RegionName')


rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbCluster')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('DbSecret')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)

database_name = "usermodule"


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
        response = rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=createSql
        )
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create user table::::::::::  ", e)
    payload = json.loads(message['body'])

    # Extract values from the payload
    firstName = payload['firstName']
    lastName = payload['lastName']
    userName = payload['userName']
    email = payload['email']
    randomId = randint(1, 1000)

    insertSql = f"INSERT INTO user (id,firstName, lastName, userName,email) VALUES ({randomId},'{firstName}', '{lastName}','{userName}','{email}')"
    # response = {"records": {}}
    try:
        rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=insertSql
        )
        """
           Create user forcefully confirm the user mail also and generate random password.
           """
        response = client.admin_create_user(
            UserPoolId=UserPool,
            Username=payload['email'],
            MessageAction='SUPPRESS',
        )

        """
        Set the actual password to the user
        """
        client.admin_set_user_password(
            UserPoolId=UserPool,
            Username=payload['email'],
            Password=payload['password'],
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


