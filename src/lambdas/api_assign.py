import json

from rds_data import execute_statement


def lambda_handler(event, context):
    payload = json.loads(event['body'])

    # Extract values from the payload
    apiUrl = payload['apiUrl']
    roleName = payload['roleName']

    insertSql = f"INSERT INTO role_api (roleName,apiUrl) VALUES ('{roleName}','{apiUrl}')"
    try:
        execute_statement(insertSql)
        return {"statusCode": 200,
                'body': json.dumps({"message": "Successfully Inserted"}),
                # "location": ip.text.replace("\n", "")

                }
    except Exception as e:
        print("Exception to insert in role_api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
