import json
import os

from rds_data import execute_statement
from global_utils import get_response, dict_connection
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

    try:
        with dict_connection.cursor() as cursor:
            count_sql = f"Select count(*) as total from user;"
            sql = (
                f"select id, name, mothersName, fathersName, email, employeeId, dob, address, userType, isActive from user LIMIT {int(page_size)} OFFSET {offset};"
            )
            print(sql)
            cursor.execute(count_sql)
            temp_result = cursor.fetchone()
            print("temp_result: ", temp_result)
            result_count = temp_result.get("total", 0)

            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)

        return get_response(
            status=200,
            error=False,
            data={"total": result_count, "users": result},
        )
    except Exception as e:
        print(e)
        return get_response(
            status=400,
            error=True,
            message="Failed to get news",
        )
    finally:
        dict_connection.commit()

# print("RESPONSE:::::: ", response)
    # data = []
    # for row in response['records']:
    #     item = {}
    #     for i, value in enumerate(row):
    #         if value.get('isNull'):
    #             item[response['columnMetadata'][i]['name']] = None
    #         else:
    #             value_type = list(value.keys())[0]
    #             if value_type == 'longValue':
    #                 item[response['columnMetadata'][i]['name']] = int(value[value_type])
    #             elif value_type == 'booleanValue':
    #                 item[response['columnMetadata'][i]['name']] = bool(value[value_type])
    #             else:
    #                 item[response['columnMetadata'][i]['name']] = value[value_type]
    #     data.append(item)
    #
    # json_data = json.dumps(data)
    # return {
    #     'statusCode': 200,
    #     'body': json_data
    # }

