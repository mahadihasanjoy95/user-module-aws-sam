import json


def lambda_handler(event, context):
    return {
        "Status": "SUCCESS",
        "Data": {
            "OutputName1": "Value1",
            "OutputName2": "Value2",
        }
    }
