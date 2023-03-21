import json

from rds_data import execute_statement


def lambda_handler(event, context):
    createSql = "CREATE TABLE  IF NOT EXISTS role_api ( roleName varchar(255) NOT NULL, apiUrl varchar(255) NOT NULL, PRIMARY KEY (roleName,apiUrl), FOREIGN KEY (roleName) REFERENCES role(roleName), FOREIGN KEY (apiUrl) REFERENCES api(apiUrl));"
    try:
        response = execute_statement(createSql)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create role_api table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    apiUrl = payload['apiUrl']
    roleName = payload['roleName']

    insertSql = f"INSERT INTO role_api (roleName,apiUrl) VALUES ('{roleName}','{apiUrl}')"
    # response = {"records": {}}
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
