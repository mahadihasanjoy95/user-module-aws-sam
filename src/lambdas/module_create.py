import json
from random import randint

from rds_data import execute_statement


def lambda_handler(event, context):
    createSql = "CREATE TABLE IF NOT EXISTS module ( id int NOT NULL, moduleName varchar(255) NOT NULL, isMenu TINYINT(1) NOT NULL, PRIMARY KEY (id));"
    try:
        execute_statement(createSql)
    except Exception as e:
        print("Exception to create module table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    moduleName = payload['moduleName']
    isMenu = payload['isMenu']
    randomId = randint(1, 1000)

    insertSql = f"INSERT INTO module (id,moduleName, isMenu) VALUES ({randomId},'{moduleName}', {isMenu})"
    response = {"records": {}}
    try:
        response = execute_statement(insertSql)
        return {"statusCode": 200,
                'body': json.dumps({"message": "Successfully Inserted"}),
                # "location": ip.text.replace("\n", "")

                }
    except Exception as e:
        print("Exception to insert in module table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
