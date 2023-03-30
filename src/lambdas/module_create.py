import json

from rds_data import execute_statement


def lambda_handler(event, context):
    payload = json.loads(event['body'])

    # Extract values from the payload
    moduleName = payload['moduleName']
    isMenu = payload['isMenu']
    # randomId = randint(1, 1000)

    insertSql = f"INSERT INTO module (moduleName, isMenu) VALUES ('{moduleName}', {isMenu})"
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
