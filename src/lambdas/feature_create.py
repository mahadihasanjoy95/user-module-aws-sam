import json
from random import randint

from rds_data import execute_statement


def lambda_handler(event, context):
    createSql = "CREATE TABLE  IF NOT EXISTS feature ( id int NOT NULL, featureName varchar(255) NOT NULL, isMenu TINYINT(1) NOT NULL, moduleId int NOT NULL, PRIMARY KEY (id), FOREIGN KEY (moduleId) REFERENCES module(id));"
    try:
        response = execute_statement(createSql)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create feature table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    featureName = payload['featureName']
    isMenu = payload['isMenu']
    moduleId = payload['moduleId']
    randomId = randint(1, 1000)

    insertSql = f"INSERT INTO feature (id,featureName, isMenu, moduleId) VALUES ({randomId},'{featureName}', {isMenu},{moduleId})"
    # response = {"records": {}}
    try:
        execute_statement(insertSql)
        return {"statusCode": 200,
                'body': json.dumps({"message": "Successfully Inserted"}),
                # "location": ip.text.replace("\n", "")

                }
    except Exception as e:
        print("Exception to insert in feature table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
