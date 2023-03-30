import os
import boto3

rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbArn')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('SecretArn')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)

database_name = "usermodule"


def execute_statement(sql, param=None):
    try:
        if param is None:
            response = rds_client.execute_statement(
                secretArn=db_credentials_secrets_arn,
                resourceArn=db_cluster_arn,
                database=database_name,
                sql=sql,
                includeResultMetadata=True
            )
        else:
            response = rds_client.execute_statement(
                secretArn=db_credentials_secrets_arn,
                resourceArn=db_cluster_arn,
                database=database_name,
                sql=sql,
                parameters=param,
                includeResultMetadata=True
            )
        return response
    except Exception as e:
        print(str(e))
        raise e
