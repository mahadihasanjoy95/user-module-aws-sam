import json
import os

import boto3
from random import randint

rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbCluster')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('DbSecret')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)

database_name = "usermodule"


def lambda_handler(event, context):
    createSql = "CREATE TABLE [IF NOT EXISTS] module ( id int NOT NULL, moduleName varchar(255) NOT NULL, isMenu TINYINT(1) NOT NULL, PRIMARY KEY (id));"
    try:
        rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=createSql
        )
    except Exception as e:
        print("Exception to create module table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    moduleName = payload['moduleName']
    isMenu = payload['isMenu']
    randomId = randint(1, 1000)

    insertSql = f"INSERT INTO module (id,moduleName, isMenu) VALUES ({randomId},'{moduleName}', {isMenu})"
    response = {"records": {}}
    try:
        response = rds_client.execute_statement(
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
        print("Exception to create module table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
