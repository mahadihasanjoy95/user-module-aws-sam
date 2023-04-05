import json
import os

import boto3
from rds_data import execute_statement
from global_utils import get_response, dict_connection
cognito_client = boto3.client('cognito-idp')
UserPool = os.getenv('UserPool')


def lambda_handler(event, context):
    payload = json.loads(event['body'])

    # Extract values from the payload
    userId = payload['userId']
    role_name = payload['roleName']

    try:
        with dict_connection.cursor() as cursor:
            sqlForFetchEmail = f"SELECT email FROM user WHERE id = {userId}"

            insertSql = f"INSERT INTO user_role (userId,roleName) VALUES ({userId},'{role_name}')"

            cursor.execute(sqlForFetchEmail)
            print(insertSql)
            rows = cursor.fetchall()
            print(sqlForFetchEmail)
            email = ""
            for row in rows:
                print("ROWS:::: ", row)
                email = row['email']
                print("Email:::::::::::: ", email)
            cursor.execute(insertSql)
            cognito_client.admin_add_user_to_group(UserPoolId=UserPool, Username=email, GroupName=role_name)
            return get_response(
                status=200,
                error=False,
                data={"message": "Successfully Assigned!!!"},
            )
    except Exception as e:
        print("Exception::::::::: ", e)
        return get_response(
            status=400,
            error=True,
            message="Failed to get news",
        )
    finally:
        dict_connection.commit()
    # response = execute_statement(sqlForFetchEmail, parametersForUser)
    #
    # # parse user email from response
    # user_email = None
    # for row in response['records']:
    #     user_email = row[0]['stringValue']
    # print("USER EMAIL::::::::::::::: ", user_email)

    # insertSql = f"INSERT INTO user_role (userId,roleName) VALUES ({userId},'{role_name}')"
    # # response = {"records": {}}
    # try:
    #     execute_statement(insertSql)
    #     """
    #     Assign role to user
    #     """
    #     cognito_client.admin_add_user_to_group(UserPoolId=UserPool, Username=user_email, GroupName=role_name)

    #     return {"statusCode": 200,
    #             'body': json.dumps({"message": "Successfully Inserted"}),
    #             # "location": ip.text.replace("\n", "")
    #
    #             }
    #
    # except Exception as e:
    #     print("Exception to insert in user_role table::::::::::  ", e)
    #     return {"statusCode": 400,
    #             'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
    #             # "location": ip.text.replace("\n", "")
    #
    #             }
