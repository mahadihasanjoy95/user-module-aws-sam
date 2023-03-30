import json

from rds_data import execute_statement


def lambda_handler(event, context):
    payload = json.loads(event['body'])

    # Extract values from the payload
    apiName = payload['apiName']
    apiUrl = payload['apiUrl']
    featureId = payload['featureId']

    insertSql = f"INSERT INTO api (apiName, apiUrl, featureId) VALUES ('{apiName}', '{apiUrl}',{featureId})"

    try:
        execute_statement(insertSql)
        return {"statusCode": 200,
                'body': json.dumps({"message": "Successfully Inserted"}),
                # "location": ip.text.replace("\n", "")

                }
    except Exception as e:
        print("Exception to insert in api table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
