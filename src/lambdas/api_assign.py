import json
import os
from random import randint

import boto3

rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbCluster')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('DbSecret')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)

database_name = "usermodule"


def lambda_handler(event, context):
    createSql = "CREATE TABLE  IF NOT EXISTS role_api ( roleName varchar(255) NOT NULL, apiUrl varchar(255) NOT NULL, PRIMARY KEY (roleName,apiUrl), FOREIGN KEY (roleName) REFERENCES role(roleName), FOREIGN KEY (apiUrl) REFERENCES api(apiUrl));"
    try:
        response = rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=createSql
        )
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create role_api table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    apiUrl = payload['apiUrl']
    roleName = payload['roleName']

    insertSql = f"INSERT INTO role_api (roleName,apiUrl) VALUES ('{roleName}','{apiUrl}')"
    # response = {"records": {}}
    try:
        rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=insertSql
        )
        return {"statusCode": 200,
                'body': json.dumps({"message": "Successfully Inserted"}),
                # "location": ip.text.replace("\n", "")

                }
    except Exception as e:
        print("Exception to insert in role_api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
