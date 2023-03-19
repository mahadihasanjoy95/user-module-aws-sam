import json
import os
from random import randint

import boto3
import requests

rds_client = boto3.client('rds-data')
db_cluster_arn = os.getenv('DbCluster')
print("DBCLUSTER::::::::::: ", db_cluster_arn)
db_credentials_secrets_arn = os.getenv('DbSecret')
print("DB SECRET::::::::::: ", db_credentials_secrets_arn)

database_name = "usermodule"


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))

    # Extract the resource properties from the event object
    resource_properties = event['ResourceProperties']

    # Perform the necessary actions based on the event type
    if event['RequestType'] == 'Create':
        # Perform resource creation logic here
        response_data = {'OutputKey': 'OutputValue'}
        send_response(event, context, "SUCCESS", response_data)
    elif event['RequestType'] == 'Update':
        # Perform resource update logic here
        response_data = {'OutputKey': 'UpdatedOutputValue'}
        send_response(event, context, "SUCCESS", response_data)
    elif event['RequestType'] == 'Delete':
        # Perform resource deletion logic here
        send_response(event, context, "SUCCESS")
def send_response(event, context, response_status, response_data=None):
    response_url = event['ResponseURL']

    response_body = {
        'Status': response_status,
        'PhysicalResourceId': context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId']
    }

    if response_data is not None:
        response_body['Data'] = response_data

    json_response_body = json.dumps(response_body)

    headers = {
        'content-type': '',
        'content-length': str(len(json_response_body))
    }

    response = boto3.client('logs').create_log_group(logGroupName='cloudformation/custom-resource')
    print("Log group created: " + str(response))

    response = boto3.client('logs').create_log_stream(logGroupName='cloudformation/custom-resource', logStreamName=context.log_stream_name)
    print("Log stream created: " + str(response))
    try:
        response = requests.put(response_url, data=json_response_body, headers=headers)
        print("CloudFormation returned status code: " + str(response.status_code))
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))
