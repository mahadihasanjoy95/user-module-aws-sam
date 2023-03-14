# import json
# import os
#
# import boto3
#
# client = boto3.client('cognito-idp')
#
# UserPool = os.getenv('UserPool')
# DynamoTableName = os.getenv('DynamoTableName')
# RegionName = os.getenv('RegionName')
#
#
# def lambda_handler(message, context):
#     """
#     This part will just check that the request is post method
#     TODO: there should be validation with powertool and pydantic
#     """
#     if ('body' not in message or
#             message['httpMethod'] != 'POST'):
#         return {
#             'statusCode': 400,
#             'headers': {},
#             'body': json.dumps({'msg': 'Bad Request'})
#         }
#     """
#     TODO: This database part should be optimized & have to Check that role exists in DB or not
#     """
#     table_name = DynamoTableName
#     # region = os.environ.get('REGION', 'ap-northeast-1')
#     region = RegionName
#     item_table = boto3.resource(
#         'dynamodb',
#         region_name=region
#     )
#
#     table = item_table.Table(table_name)
#     payload = json.loads(message['body'])
#
#     params = {
#         'PK': "ROLE#",
#         'SK': payload['roleName'] + "#",
#         'role_desc': payload['roleDesc']
#     }
#     table.put_item(
#         TableName=table_name,
#         Item=params
#     )
#     """
#     Create group into user-pool. Here group is actually define the role
#     """
#     reply = client.create_group(UserPoolId=UserPool, GroupName=payload['roleName'])
#     return {
#         "statusCode": 200,
#         "headers": {},
#         'body': json.dumps(reply, indent=4, sort_keys=True, default=str),  # default=decimal_default),
#     }

import json
import os
from random import randint

import boto3

rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbCluster')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('DbSecret')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)
UserPool = os.getenv('UserPool')
database_name = "usermodule"

client = boto3.client('cognito-idp')
def lambda_handler(event, context):
    createSql = "CREATE TABLE  IF NOT EXISTS role (roleName varchar(255) NOT NULL, roleDescription varchar(255) NOT NULL, PRIMARY KEY (roleName));"
    try:
        response = rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=createSql
        )
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create role table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    roleName = payload['roleName']
    roleDescription = payload['roleDescription']

    insertSql = f"INSERT INTO role (roleName, roleDescription) VALUES ('{roleName}', '{roleDescription}')"
    # response = {"records": {}}
    try:
        rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=insertSql
        )
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
