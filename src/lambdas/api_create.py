import os

import boto3

rds_client = boto3.client('rds')
cluster_arn = os.getenv('DbCluster')
secret_arn = os.getenv('DbSecret')

rdsData = boto3.client('rds-data')
database = "user_module"

response1 = rdsData.execute_statement(
    resourceArn=cluster_arn,
    secretArn=secret_arn,
    database=database,
    sql='')
print(response1)
