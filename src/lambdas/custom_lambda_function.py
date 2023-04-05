import json
import os

import boto3
import global_utils as gb_utils
UserPool = os.getenv('UserPool')

client = boto3.client('cognito-idp')
db_settings_initialization = "ALTER DATABASE {} CHARACTER SET utf8;"

userTable = "CREATE TABLE  IF NOT EXISTS user " \
            "( " \
            "id int NOT NULL AUTO_INCREMENT, " \
            "name varchar(255) NOT NULL, " \
            "mothersName varchar(255), " \
            "fathersName varchar(255), " \
            "email varchar(255) NOT NULL, " \
            "employeeId varchar(255), " \
            "dob DATE NOT NULL," \
            "address varchar(500)," \
            "userType varchar(50) NOT NULL," \
            "isActive BOOLEAN NOT NULL," \
            "imageLink varchar(255)," \
            "phoneNumber varchar(255)," \
            "createdAt DATE," \
            "updatedAt DATE," \
            "PRIMARY KEY (id));"
addressTable = "CREATE TABLE IF NOT EXISTS address " \
               "( " \
               "area varchar(255), " \
               "postOffice varchar(255), " \
               "thana varchar(255), " \
               "district varchar(255) , " \
               "postCode int, " \
               "addresype varchar(255) , " \
               "userId int NOT NULL, " \
               "FOREIGN KEY (userId) REFERENCES user(id));"

roleTable = "CREATE TABLE  IF NOT EXISTS role " \
                "(" \
                "roleName varchar(255) NOT NULL, " \
                "roleDescription varchar(255) NOT NULL, " \
                "isActive BOOLEAN NOT NULL," \
                "PRIMARY KEY (roleName));"
moduleTable = "CREATE TABLE IF NOT EXISTS module " \
                  "( " \
                  "id int NOT NULL AUTO_INCREMENT, " \
                  "moduleName varchar(255) NOT NULL, " \
                  "isMenu TINYINT(1) NOT NULL, " \
                  "PRIMARY KEY (id));"
featureTable = "CREATE TABLE  IF NOT EXISTS feature " \
                   "( " \
                   "id int NOT NULL AUTO_INCREMENT, " \
                   "featureName varchar(255) NOT NULL, " \
                   "isMenu TINYINT(1) NOT NULL, " \
                   "moduleId int NOT NULL, " \
                   "PRIMARY KEY (id), " \
                   "FOREIGN KEY (moduleId) REFERENCES module(id));"
apiTable = "CREATE TABLE  IF NOT EXISTS api " \
               "(" \
               "apiName varchar(255) NOT NULL, " \
               "apiUrl varchar(255) NOT NULL, " \
               "featureId int NOT NULL, " \
               "PRIMARY KEY (apiUrl), " \
               "FOREIGN KEY (featureId) REFERENCES feature(id));"
userRoleTable = "CREATE TABLE  IF NOT EXISTS user_role " \
                    "( " \
                    "userId int NOT NULL, " \
                    "roleName varchar(255) NOT NULL, " \
                    "assignedBy int, " \
                    "PRIMARY KEY (userId,roleName), " \
                    "FOREIGN KEY (userId) REFERENCES user(id), " \
                    "FOREIGN KEY (roleName) REFERENCES role(roleName));"
roleApiTable = "CREATE TABLE  IF NOT EXISTS role_api " \
                   "( " \
                   "roleName varchar(255) NOT NULL, " \
                   "apiUrl varchar(255) NOT NULL, " \
                   "PRIMARY KEY (roleName,apiUrl), " \
                   "FOREIGN KEY (roleName) REFERENCES role(roleName), " \
                   "FOREIGN KEY (apiUrl) REFERENCES api(apiUrl));"
insertRoleSql = f"INSERT INTO role (roleName, roleDescription, isActive) VALUES ('admin', 'This is the super user of the system', TRUE)"
client.create_group(UserPoolId=UserPool, GroupName="admin")
def lambda_handler(event, context):
    connection = gb_utils.connection
    connection.begin()

    try:
        with connection.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS=0")
            cur.execute(db_settings_initialization.format(gb_utils.database_name))
            cur.execute(userTable)
            cur.execute(addressTable)
            cur.execute(roleTable)
            cur.execute(moduleTable)
            cur.execute(featureTable)
            cur.execute(userRoleTable)
            cur.execute(roleApiTable)
            cur.execute(insertRoleSql)
            cur.execute("SET FOREIGN_KEY_CHECKS=1")
        connection.commit()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "error": False,
                "message": "created all tables",
            }),
        }
    except Exception as e:
        print(e)
        connection.rollback()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "error": True,
                "message": "failed to create tables",
            }),
        }
