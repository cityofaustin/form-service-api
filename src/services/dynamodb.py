import json, boto3
from flask import jsonify

from services.helpers import getCurrentDateTime
from env import *

if(DEPLOYMENT_MODE == "LOCAL"):
    # Initialize Client
    dynamodb_client = boto3.client('dynamodb', region_name=DEFALUT_REGION, aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
else:
    # We should already have access to these resources
    dynamodb_client = boto3.client('dynamodb', region_name=DEFALUT_REGION)

# Get an existing item from dynamodb
def get_dynamodb_item(id):
    print("get_dynamodb_item() Id: " + id)

    dynamodb_response = dynamodb_client.get_item(
        TableName=LOG_TABLE,
        Key={
            'id': { 'S': str(id) }
        }
    )
    item = dynamodb_response.get('Item')
    if not item:
        return None
    return item

# Post a new item to dynamodb
def create_dynamodb_item(id, form_type, data=None):
    # Stringify json form data
    if (data):
        if (not isinstance(inputJson, str)):
            stringified_data = json.dumps(data)
        else:
            stringified_data = data
    else:
        stringified_data = None

    # TODO: will this throw an error on duplication?
    dynamodb_client.put_item(
        TableName=LOG_TABLE,
        ConditionExpression='attribute_not_exists(id)',
        Item={
            'id': {'S': id},
            'created_at': {'S': getCurrentDateTime()},
            'form_type': {'S': form_type},
            'data': { 'S': stringified_data }
        }
    )
