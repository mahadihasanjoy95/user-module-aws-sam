import json
import os
from collections import namedtuple

from rds_data import execute_statement

DynamoTableName = os.getenv('DynamoTableName')
RegionName = os.getenv('RegionName')


# Define the function to convert the namedtuple to a dictionary
def namedtuple_to_dict(obj):
    return obj._asdict()


def lambda_handler(message, context):
    if ('httpMethod' not in message or
            message['httpMethod'] != 'GET'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    response = []
    res = execute_statement("select * from user")
    print("RESPONSE:::::: ", res)
    User = namedtuple('User', ['id', 'firstName', 'lastName', 'userName', 'email'])
    for record in res['records']:
        print()
        row_data = []
        for data_dict in record:
            # print(data_dict)
            for data_type, data_value in data_dict.items():
                row_data.append(data_value)
        response.append(User(*row_data))

    print(response)

    return {
        "statusCode": 200,
        "headers": {},
        'body': json.dumps(response)  # default=decimal_default),
    }
