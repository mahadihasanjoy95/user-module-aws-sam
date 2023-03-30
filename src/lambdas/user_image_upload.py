import json

from rds_data import execute_statement


def lambda_handler(message, context):
    if ('body' not in message or
            message['httpMethod'] != 'POST'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }
    payload = json.loads(message['body'])

    # Extract values from the payload
    userId = payload['userId']
    imageLink = payload['imageLink']

    editSql = f"UPDATE user SET imageLink = '{imageLink}'  WHERE id  = {userId};"
    try:
        execute_statement(editSql)
        return {
            "statusCode": 200,
            "headers": {},
            'body': json.dumps({"message": "Successfully Updated!"}, indent=4, sort_keys=True, default=str),
            # default=decimal_default),
        }
    except Exception as e:
        print("Exception to update in user table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't update the data in user tableh!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }

