import cfnresponse
from rds_data import execute_statement


def lambda_handler(event, context):
    # arn:aws:s3:::my-bucket-water
    # sql_statement = f"ALTER TABLE user ADD COLUMN imageLink varchar(255)"
    # try:
    #     response = execute_statement(sql_statement)
    #     print("RESPONSE::::::::::::::::: ", response)
    # except Exception as e:
    #     print("Exception to alter user table::::::::::  ", e)
    print(event)
    print("Lambda triggered!!!!!!!!!!")
    """
    Insert Aurora MySQL part
    """
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
                "PRIMARY KEY (id));"
    try:
        response = execute_statement(userTable)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create user table::::::::::  ", e)
    roleTable = "CREATE TABLE  IF NOT EXISTS role " \
                "(" \
                "roleName varchar(255) NOT NULL, " \
                "roleDescription varchar(255) NOT NULL, " \
                "PRIMARY KEY (roleName));"
    try:
        response = execute_statement(roleTable)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create role table::::::::::  ", e)

    moduleTable = "CREATE TABLE IF NOT EXISTS module " \
                  "( " \
                  "id int NOT NULL AUTO_INCREMENT, " \
                  "moduleName varchar(255) NOT NULL, " \
                  "isMenu TINYINT(1) NOT NULL, " \
                  "PRIMARY KEY (id));"
    try:
        response = execute_statement(moduleTable)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create module table::::::::::  ", e)
    featureTable = "CREATE TABLE  IF NOT EXISTS feature " \
                   "( " \
                   "id int NOT NULL AUTO_INCREMENT, " \
                   "featureName varchar(255) NOT NULL, " \
                   "isMenu TINYINT(1) NOT NULL, " \
                   "moduleId int NOT NULL, " \
                   "PRIMARY KEY (id), " \
                   "FOREIGN KEY (moduleId) REFERENCES module(id));"
    try:
        response = execute_statement(featureTable)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create feature table::::::::::  ", e)

    apiTable = "CREATE TABLE  IF NOT EXISTS api " \
               "(" \
               "apiName varchar(255) NOT NULL, " \
               "apiUrl varchar(255) NOT NULL, " \
               "featureId int NOT NULL, " \
               "PRIMARY KEY (apiUrl), " \
               "FOREIGN KEY (featureId) REFERENCES feature(id));"
    try:
        response = execute_statement(apiTable)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create api table::::::::::  ", e)
    userRoleTable = "CREATE TABLE  IF NOT EXISTS user_role " \
                    "( " \
                    "userId int NOT NULL, " \
                    "roleName varchar(255) NOT NULL, " \
                    "assignedBy int, " \
                    "PRIMARY KEY (userId,roleName), " \
                    "FOREIGN KEY (userId) REFERENCES user(id), " \
                    "FOREIGN KEY (roleName) REFERENCES role(roleName));"
    try:
        response = execute_statement(userRoleTable)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create user_role table::::::::::  ", e)

    roleApiTable = "CREATE TABLE  IF NOT EXISTS role_api " \
                   "( " \
                   "roleName varchar(255) NOT NULL, " \
                   "apiUrl varchar(255) NOT NULL, " \
                   "PRIMARY KEY (roleName,apiUrl), " \
                   "FOREIGN KEY (roleName) REFERENCES role(roleName), " \
                   "FOREIGN KEY (apiUrl) REFERENCES api(apiUrl));"
    try:
        response = execute_statement(roleApiTable)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to create role_api table::::::::::  ", e)
    insertRoleSql = f"INSERT INTO role (roleName, roleDescription) VALUES ('admin', 'This is the super user of the system')"
    try:
        response = execute_statement(insertRoleSql)
        print("RESPONSE::::::::::::::::: ", response)
    except Exception as e:
        print("Exception to insert in role table::::::::::  ", e)

    cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
