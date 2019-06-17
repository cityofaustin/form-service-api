import json, boto3
from flask import jsonify

from services.helpers import getCurrentDateTime
import env

# Get an existing item from dynamodb
def get_dynamodb_item(id):
    print("get_dynamodb_item() Id: " + id)

    dynamodb_response = env.dynamodb_client.get_item(
        TableName=env.LOG_TABLE,
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
    env.dynamodb_client.put_item(
        TableName=env.LOG_TABLE,
        ConditionExpression='attribute_not_exists(id)',
        Item={
            'id': {'S': id},
            'created_at': {'S': getCurrentDateTime()},
            'form_type': {'S': form_type},
            'data': { 'S': stringified_data }
        }
    )
