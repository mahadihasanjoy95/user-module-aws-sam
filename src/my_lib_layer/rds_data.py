import os
import boto3

rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbArn')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('SecretArn')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)

database_name = "usermodule"


def execute_statement(sql):
    try:
        response = rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            resourceArn=db_cluster_arn,
            database=database_name,
            sql=sql,
            includeResultMetadata=False
        )
        return response
    except Exception as e:
        print(str(e))
        raise e
