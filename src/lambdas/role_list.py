import json
import os
from collections import namedtuple

from rds_data import execute_statement


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
    params = message['queryStringParameters']
    page_size = params.get('limit')
    page_number = params.get('offset')
    data = []
    offset = (int(page_number) - 1) * int(page_size)
    parameters = [
        {'name': 'page_size', 'value': {'longValue': int(page_size)}},
        {'name': 'offset', 'value': {'longValue': offset}}
    ]
    response = execute_statement("select * from role LIMIT :page_size OFFSET :offset", parameters)
    print("RESPONSE:::::: ", response)
    data = []
    for row in response['records']:
        item = {}
        for i, value in enumerate(row):
            item[response['columnMetadata'][i]['name']] = value['stringValue']
        data.append(item)

    return {
        'statusCode': 200,
        'body': json.dumps(data)
    }
