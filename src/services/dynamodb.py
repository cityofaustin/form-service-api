import json, boto3, botocore, datetime
from flask import jsonify
from botocore.exceptions import ClientError

from services.helpers import getCurrentDateTime, generate_random_hash
import env

if(env.DEPLOYMENT_MODE == "LOCAL"):
    # Initialize S3 Client
    dynamodb_client = boto3.client('dynamodb', region_name=env.DEFALUT_REGION, aws_access_key_id=env.S3_KEY, aws_secret_access_key=env.S3_SECRET)
else:
    # We should already have access to these resources
    dynamodb_client = boto3.client('dynamodb', region_name=env.DEFALUT_REGION)

# Get an existing item from dynamodb
def get_dynamodb_item(id):
    print("get_dynamodb_item() Id: " + id)

    dynamodb_response = dynamodb_client.get_item(
        TableName=env.DYNAMO_DB_TABLE,
        Key={
            'id': { 'S': str(id) }
        }
    )
    item = dynamodb_response.get('Item')
    if not item:
        return None
    return item

# Post a new item to dynamodb
# Returns a newly generated case_number
def create_dynamodb_item(form_type, data={}):
    # Generate random case_number until a unique one is found
    # Check that case_number is not already used in dynamodb
    while True:
        datestr = datetime.datetime.now().strftime('%Y-%m%d-')
        rndstr = generate_random_hash()[0:4]
        case_number = f"{datestr}{rndstr}"
        item = get_dynamodb_item(case_number) # Record is 'None' if not found.
        if (not item):
            break

    # Save case_number as "id" to ensure that user confirmation/case numbers are unique
    try:
        dynamodb_client.put_item(
            TableName=env.DYNAMO_DB_TABLE,
            ConditionExpression='attribute_not_exists(id)',
            Item={
                'id': {'S': str(case_number)},
                'created_at': {'S': getCurrentDateTime()},
                'form_type': {'S': form_type},
                'data': { 'M': data }
            }
        )
    # If a duplicate case_number was created asynchronously by another process (between "while True" loop and "dynamodb_client.put_item"),
    # then generate another case_number
    except ClientError as e:
        if 'ConditionalCheckFailedException' == e.__class__.__name__:
            print("Duplicate case_number, trying again")
            return create_dynamodb_item(form_type, data)
        else:
            raise e
    except Exception as e:
        raise e
    else:
        return case_number
