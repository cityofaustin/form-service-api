import os, boto3

#####
# Environment Variables
#####
DEPLOYMENT_MODE           = os.getenv("DEPLOYMENT_MODE", "LOCAL")
ALLOWED_IMAGE_EXTENSIONS  = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS        = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

S3_KEY                    = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET                 = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET                 = os.getenv("AWS_BUCKET_NAME")
S3_LOCATION               = f'http://{S3_BUCKET}.s3.amazonaws.com/'
DEFALUT_REGION            = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
LOG_TABLE                 = os.getenv("PM_LOGTABLE", "coa-forms-dev")

EMAIL_ADDRESS_OPO         = os.getenv("EMAIL_ADDRESS_OPO")
EMAIL_ADDRESS_APD         = os.getenv("EMAIL_ADDRESS_APD")
EMAIL_ADDRESS_REPLYTO     = os.getenv("EMAIL_ADDRESS_REPLYTO")
EMAIL_ADDRESS_SMOKE_TEST  = "nick.ivons@austintexas.gov"

#####
# 3rd Party Configs
#####

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
