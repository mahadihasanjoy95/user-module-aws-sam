import json
import os
import re
import time
import urllib.request

import boto3
from jose import jwk, jwt
from jose.utils import base64url_decode
from rds_data import execute_statement
from global_utils import get_response, dict_connection

UserPoolClient = os.getenv('UserPoolClient')
UserPool = os.getenv('UserPool')
RegionName = os.getenv('RegionName')

region = RegionName
keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, UserPool)

with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']


def auth_token_decode(token, api):
    """
        Checks whether JWT Token is valid or not.
        If valid returns True else False
    """
    try:
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']
        # search for the kid in the downloaded public keys
        key_index = -1
        for i in range(len(keys)):
            if kid == keys[i]['kid']:
                key_index = i
                break
        if key_index == -1:
            print('Public key not found in jwks.json')
            return False
        public_key = jwk.construct(keys[key_index])

        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
        # verify the signature
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            print('Signature verification failed')
            return False
        print('Signature successfully verified')
        # since we passed the verification, we can now safely
        # use the unverified claims
        claims = jwt.get_unverified_claims(token)
        print(claims)
        # additionally we can verify the token expiration
        if time.time() > claims['exp']:
            print('Token is expired')
            return False
        # and the Audience  (use claims['client_id'] if verifying an access token)
        if claims['aud'] != UserPoolClient:
            print('Token was not issued for this audience')
            return False
        # TODO: This section will be enabled after adding role and permission from DB layer
        # return check_role_permission_dynamoDb(claims["cognito:groups"][0], api)
        print("CLAIMS:::::::::::::::::: ", claims)
        return check_role_permission_rds(claims["cognito:groups"][0], api)
        # return True
    except Exception as e:
        print("NEW EXCEPTION:::::::::::::::::::: ", e)
        return False


def check_role_permission_rds(role, api):
    if role == "admin":
        return True
    """
    Check the api has the role wise permission from RDS here
    """
    try:
        # Split the method ARN to retrieve the API path
        arn_parts = api.split('/')
        api_path = '/' + '/'.join(arn_parts[3:])

        # Log the extracted API path
        print(f"API path::::::::::::::::::: {api_path}")

        # Check that this role and path exists in role_api table or not
        # Check if the row exists
        sql_query = f'SELECT 1 FROM role_api WHERE roleName = \'{role}\' AND apiUrl = \'{api_path}\''
        # response = execute_statement(sql_query)
        # print("DB RESPONSE:::::::: ", response['records'])
        # # If the SELECT query returns any rows, then the row exists
        # row_exists = len(response['records']) > 0
        #
        # # Return a response indicating whether the row exists or not
        # if row_exists:
        #     return True
        # else:
        #     return False
        try:
            with dict_connection.cursor() as cursor:
                cursor.execute(sql_query)
                result = cursor.fetchall()
                print("Hey!!! This is the Result:::::::::::::::::::::", result)
                return True
        except Exception as e:
            print("Exception from the RDS::::::::::  ", e)
            return False
        finally:
            dict_connection.commit()
    except Exception as e:
        print("Exception from the RDS::::::::::  ", e)
        return False


def check_role_permission_dynamoDb(role, api):
    """
    Check the api has the role wise permission from DynamoDB here
    """
    try:
        res = table.get_item(
            Key={
                'PK': "ROLE#",
                'SK': role + "#" + api
            }
        )
        # Check if the item exists
        if 'Item' in res:
            return True
        else:
            return False
    except Exception as e:
        print("Exception from the dynamoDB::::::::::  ", e)
        return False


def lambda_handler(event, context):
    token = event['authorizationToken']  # retrieve the Auth token
    # Remove Bearer from the token
    token = token.replace('Bearer ', '')
    token = token.replace('bearer  ', '')
    principal_id = 'abc123'  # fake principle
    policy = create_policy(event['methodArn'], principal_id)

    if event['authorizationToken']:
        user_info = auth_token_decode(token, event['methodArn'])
        print("USER INFO:::::: ", user_info)
        if user_info:
            policy.allowAllMethods()
        else:
            policy.denyAllMethods()
    else:
        policy.denyAllMethods()

    return policy.build()


def create_policy(method_arn, principal_id):
    tmp = method_arn.split(':')
    region = tmp[3]
    account_id = tmp[4]
    api_id, stage = tmp[5].split('/')[:2]
    policy = AuthPolicy(principal_id, account_id)
    policy.restApiId = api_id
    policy.region = region
    policy.stage = stage
    return policy


class HttpVerb:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    ALL = '*'


class AuthPolicy(object):
    # The AWS account id the policy will be generated for. This is used to create the method ARNs.
    awsAccountId = ''
    # The principal used for the policy, this should be a unique identifier for the end user.
    principalId = ''
    # The policy version used for the evaluation. This should always be '2012-10-17'
    version = '2012-10-17'
    # The regular expression used to validate resource paths for the policy
    pathRegex = '^[/.a-zA-Z0-9-\*]+$'

    '''Internal lists of allowed and denied methods.
    These are lists of objects and each object has 2 properties: A resource
    ARN and a nullable conditions statement. The build method processes these
    lists and generates the approriate statements for the final policy.
    '''
    allowMethods = []
    denyMethods = []

    # The API Gateway API id. By default this is set to '*'
    restApiId = '*'
    # The region where the API is deployed. By default this is set to '*'
    region = '*'
    # The name of the stage used in the policy. By default this is set to '*'
    stage = '*'

    def __init__(self, principal, awsAccountId):
        self.awsAccountId = awsAccountId
        self.principalId = principal
        self.allowMethods = []
        self.denyMethods = []

    def _addMethod(self, effect, verb, resource, conditions):
        '''Adds a method to the internal lists of allowed or denied methods. Each object in
        the internal list contains a resource ARN and a condition statement. The condition
        statement can be null.'''
        if verb != '*' and not hasattr(HttpVerb, verb):
            raise NameError('Invalid HTTP verb ' + verb + '. Allowed verbs in HttpVerb class')
        resourcePattern = re.compile(self.pathRegex)
        if not resourcePattern.match(resource):
            raise NameError('Invalid resource path: ' + resource + '. Path should match ' + self.pathRegex)

        if resource[:1] == '/':
            resource = resource[1:]

        resourceArn = 'arn:aws:execute-api:{}:{}:{}/{}/{}/{}'.format(self.region, self.awsAccountId, self.restApiId,
                                                                     self.stage, verb, resource)

        if effect.lower() == 'allow':
            self.allowMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })
        elif effect.lower() == 'deny':
            self.denyMethods.append({
                'resourceArn': resourceArn,
                'conditions': conditions
            })

    def _getEmptyStatement(self, effect):
        '''Returns an empty statement object prepopulated with the correct action and the
        desired effect.'''
        statement = {
            'Action': 'execute-api:Invoke',
            'Effect': effect[:1].upper() + effect[1:].lower(),
            'Resource': []
        }

        return statement

    def _getStatementForEffect(self, effect, methods):
        '''This function loops over an array of objects containing a resourceArn and
        conditions statement and generates the array of statements for the policy.'''
        statements = []

        if len(methods) > 0:
            statement = self._getEmptyStatement(effect)

            for curMethod in methods:
                if curMethod['conditions'] is None or len(curMethod['conditions']) == 0:
                    statement['Resource'].append(curMethod['resourceArn'])
                else:
                    conditionalStatement = self._getEmptyStatement(effect)
                    conditionalStatement['Resource'].append(curMethod['resourceArn'])
                    conditionalStatement['Condition'] = curMethod['conditions']
                    statements.append(conditionalStatement)

            if statement['Resource']:
                statements.append(statement)

        return statements

    def allowAllMethods(self):
        '''Adds a '*' allow to the policy to authorize access to all methods of an API'''
        self._addMethod('Allow', HttpVerb.ALL, '*', [])

    def denyAllMethods(self):
        '''Adds a '*' allow to the policy to deny access to all methods of an API'''
        self._addMethod('Deny', HttpVerb.ALL, '*', [])

    def allowMethod(self, verb, resource):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods for the policy'''
        self._addMethod('Allow', verb, resource, [])

    def denyMethod(self, verb, resource):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods for the policy'''
        self._addMethod('Deny', verb, resource, [])

    def allowMethodWithConditions(self, verb, resource, conditions):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of allowed
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition'''
        self._addMethod('Allow', verb, resource, conditions)

    def denyMethodWithConditions(self, verb, resource, conditions):
        '''Adds an API Gateway method (Http verb + Resource path) to the list of denied
        methods and includes a condition for the policy statement. More on AWS policy
        conditions here: http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html#Condition'''
        self._addMethod('Deny', verb, resource, conditions)

    def build(self):
        '''Generates the policy document based on the internal lists of allowed and denied
        conditions. This will generate a policy with two main statements for the effect:
        one statement for Allow and one statement for Deny.
        Methods that includes conditions will have their own statement in the policy.'''
        if ((self.allowMethods is None or len(self.allowMethods) == 0) and
                (self.denyMethods is None or len(self.denyMethods) == 0)):
            raise NameError('No statements defined for the policy')

        policy = {
            'principalId': self.principalId,
            'policyDocument': {
                'Version': self.version,
                'Statement': []
            }
        }

        policy['policyDocument']['Statement'].extend(self._getStatementForEffect('Allow', self.allowMethods))
        policy['policyDocument']['Statement'].extend(self._getStatementForEffect('Deny', self.denyMethods))

        return policy
