import json
import os

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
    params = message['queryStringParameters']
    page_size = params.get('limit')
    page_number = params.get('offset')
    offset = (int(page_number) - 1) * int(page_size)
    parameters = [
        {'name': 'page_size', 'value': {'longValue': int(page_size)}},
        {'name': 'offset', 'value': {'longValue': offset}}
    ]

    response = execute_statement("select id, name, mothersName, fathersName, email, employeeId, dob, address, userType, isActive from user LIMIT :page_size OFFSET :offset", parameters)
    # response = execute_statement("select id, name, mothersName, fathersName, email, employeeId, dob, address, userType, isActive, roleName from user LEFT JOIN user_role ON user.id = user_role.userId LIMIT :page_size OFFSET :offset", parameters)
    print("RESPONSE:::::: ", response)
    data = []
    for row in response['records']:
        item = {}
        for i, value in enumerate(row):
            if value.get('isNull'):
                item[response['columnMetadata'][i]['name']] = None
            else:
                value_type = list(value.keys())[0]
                if value_type == 'longValue':
                    item[response['columnMetadata'][i]['name']] = int(value[value_type])
                elif value_type == 'booleanValue':
                    item[response['columnMetadata'][i]['name']] = bool(value[value_type])
                else:
                    item[response['columnMetadata'][i]['name']] = value[value_type]
        data.append(item)

    json_data = json.dumps(data)
    return {
        'statusCode': 200,
        'body': json_data
    }
