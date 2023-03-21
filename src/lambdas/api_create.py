import json
from random import randint

from rds_data import execute_statement


def lambda_handler(event, context):
    createSql = "CREATE TABLE  IF NOT EXISTS api (apiName varchar(255) NOT NULL, apiUrl varchar(255) NOT NULL, featureId int NOT NULL, PRIMARY KEY (apiUrl), FOREIGN KEY (featureId) REFERENCES feature(id));"
    try:
        response = execute_statement(createSql)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create api table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    apiName = payload['apiName']
    apiUrl = payload['apiUrl']
    featureId = payload['featureId']
    randomId = randint(1, 1000)

    insertSql = f"INSERT INTO api (apiName, apiUrl, featureId) VALUES ('{apiName}', '{apiUrl}',{featureId})"
    # response = {"records": {}}
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
