import json
import os

import boto3

rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbCluster')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('DbSecret')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)

database_name = "usermodule"
cognito_client = boto3.client('cognito-idp')
UserPool = os.getenv('UserPool')


def lambda_handler(event, context):
    createSql = "CREATE TABLE  IF NOT EXISTS user_role ( userId int NOT NULL, roleId int NOT NULL, PRIMARY KEY (userId,roleId), FOREIGN KEY (userId) REFERENCES user(id), FOREIGN KEY (roleId) REFERENCES role(id));"
    try:
        response = rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=createSql
        )
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create user_role table::::::::::  ", e)
    payload = json.loads(event['body'])

    # Extract values from the payload
    userId = payload['userId']
    roleId = payload['roleId']

    """
    Fetch user email from USER table PART 
    """
    parametersForUser = [{'name': 'id', 'value': {'longValue': int(userId)}}]

    sqlForFetchEmail = "SELECT email FROM user WHERE id = :id"
    response = rds_client.execute_statement(
        resourceArn=db_cluster_arn,
        secretArn=db_credentials_secrets_arn,
        database=database_name,
        sql=sqlForFetchEmail,
        parameters=parametersForUser
    )

    # parse user email from response
    user_email = None
    for row in response['records']:
        user_email = row[0]['stringValue']
    print("USER EMAIL::::::::::::::: ", user_email)

    """
        Fetch role name from role table PART 
        """
    parametersForRole = [{'name': 'id', 'value': {'longValue': int(roleId)}}]

    sqlForFetchEmail = "SELECT roleName FROM role WHERE id = :id"
    response = rds_client.execute_statement(
        resourceArn=db_cluster_arn,
        secretArn=db_credentials_secrets_arn,
        database=database_name,
        sql=sqlForFetchEmail,
        parameters=parametersForRole
    )

    # parse user email from response
    role_name = None
    for row in response['records']:
        role_name = row[0]['stringValue']
    print("Role Name::::::::::::::: ", role_name)

    insertSql = f"INSERT INTO user_role (userId,roleId) VALUES ({userId},{roleId})"
    # response = {"records": {}}
    try:
        rds_client.execute_statement(
            secretArn=db_credentials_secrets_arn,
            database=database_name,
            resourceArn=db_cluster_arn,
            sql=insertSql
        )
        """
        Assign role to user
        """
        cognito_client.admin_add_user_to_group(UserPoolId=UserPool, Username=user_email, GroupName=role_name)

        return {"statusCode": 200,
                'body': json.dumps({"message": "Successfully Inserted"}),
                # "location": ip.text.replace("\n", "")

                }

    except Exception as e:
        print("Exception to insert in user_role table::::::::::  ", e)
        return {"statusCode": 400,
                'body': json.dumps({"message": "Can't insert the data!!!!!!!!"}),
                # "location": ip.text.replace("\n", "")

                }
