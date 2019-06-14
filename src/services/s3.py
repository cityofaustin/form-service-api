import boto3

from env import *

if(DEPLOYMENT_MODE == "LOCAL"):
    # Initialize S3 Client
    s3 = boto3.client("s3",region_name=DEFALUT_REGION, aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    dynamodb_client = boto3.client('dynamodb', region_name=DEFALUT_REGION, aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    ses_client = boto3.client('ses', region_name=DEFALUT_REGION, aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
else:
    # We should already have access to these resources
    s3 = boto3.client("s3", region_name=DEFALUT_REGION)
    dynamodb_client = boto3.client('dynamodb', region_name=DEFALUT_REGION)
    ses_client = boto3.client('ses', region_name=DEFALUT_REGION)
