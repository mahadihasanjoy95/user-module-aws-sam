import json
import os

import boto3
import pymysql
from aws_lambda_powertools.utilities.feature_flags import (AppConfigStore,
                                                           FeatureFlags)

# ========================== environment variables ==========================
stage_name = os.environ.get('STAGE_NAME', None)

# ========================== Feature Flags ==========================

app_config = AppConfigStore(
    environment=stage_name,
    application="Water",
    name='features'
)

feature_flags = FeatureFlags(store=app_config)

# ========================== Aurora ==========================

sm_client = boto3.client('secretsmanager')
db_secret = os.environ.get('AURORA_DB_SECRET', None)
print("DB SECRET::::::::: ", db_secret)
host = os.environ.get('AURORA_CLUSTER_HOST', None)
port = int(os.environ.get('DBPORT', 6033))
database_name = None

connection = None
dict_connection = None

if db_secret:
    print('connecting to db')
    print('host: ', host)
    sm_response = sm_client.get_secret_value(SecretId=db_secret)
    secret = json.loads(sm_response['SecretString'])
    database_name = secret['dbname']
    connection = pymysql.connect(host=host, port=port, user=secret['username'], password=secret['password'],
                                 database=secret['dbname'], connect_timeout=5)
    dict_connection = pymysql.connect(
        host=host,
        port=port,
        user=secret['username'],
        password=secret['password'],
        database=secret['dbname'],
        connect_timeout=5,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

    print(f"connection: {connection}")
    print(f"dict_connection: {dict_connection}")


def get_response(status=400, error=True, code="GENERIC", message="NA", data={}, headers={}):
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }
    final_headers = {**default_headers, **headers}
    return {
        "statusCode": status,
        "headers": final_headers,
        "body": json.dumps({
            "error": error,
            "code": code,
            "message": message,
            "data": data
        }, default=str),  # default=decimal_default),
    }


def get_formatted_validation_error(e):
    errors = []
    try:
        for err in e.errors():
            errors.append(f"{err['loc'][0]}: {err['msg']}")
    except Exception as exp:
        print(exp)

    return ','.join(errors)
