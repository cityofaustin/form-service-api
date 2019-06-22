import os

#####
# Environment Variables
#####
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local")

if (DEPLOYMENT_MODE == "production"):
    # Common
    DYNAMO_DB_TABLE="coa-forms-prod"
    S3_UPLOADS_BUCKET=os.getenv("S3_UPLOADS_BUCKET_PROD")
    EMAIL_SMOKE_TEST=os.getenv("EMAIL_SMOKE_TEST_PROD")
    # OPO
    EMAIL_OPO=os.getenv("EMAIL_OPO_PROD")
    EMAIL_APD=os.getenv("EMAIL_APD_PROD")
    EMAIL_OPO_REPLYTO=os.getenv("EMAIL_REPLYTO_PROD")
elif (DEPLOYMENT_MODE == "staging"):
    # Common
    DYNAMO_DB_TABLE="coa-forms-dev"
    S3_UPLOADS_BUCKET=os.getenv("S3_UPLOADS_BUCKET_STAGING")
    EMAIL_SMOKE_TEST=os.getenv("EMAIL_SMOKE_TEST_STAGING")
    # OPO
    EMAIL_OPO=os.getenv("EMAIL_OPO_STAGING")
    EMAIL_APD=os.getenv("EMAIL_APD_STAGING")
    EMAIL_OPO_REPLYTO=os.getenv("EMAIL_REPLYTO_STAGING")
elif (DEPLOYMENT_MODE == "dev"):
    # Common
    DYNAMO_DB_TABLE="coa-forms-dev"
    S3_UPLOADS_BUCKET="coa-forms-uploads-pr"
    EMAIL_SMOKE_TEST=os.getenv("EMAIL_SMOKE_TEST_STAGING")
    # OPO
    EMAIL_OPO=os.getenv("EMAIL_OPO_STAGING")
    EMAIL_APD=os.getenv("EMAIL_APD_STAGING")
    EMAIL_OPO_REPLYTO=os.getenv("EMAIL_REPLYTO_STAGING")
elif (DEPLOYMENT_MODE == "local"):
    # Common
    DYNAMO_DB_TABLE=os.getenv("COA_FORMS_DYNAMO_DB_TABLE")
    S3_UPLOADS_BUCKET=os.getenv("COA_FORMS_S3_UPLOADS_BUCKET")
    EMAIL_SMOKE_TEST=os.getenv("COA_FORMS_EMAIL_SMOKE_TEST")
    # OPO
    EMAIL_OPO=os.getenv("COA_FORMS_EMAIL_OPO")
    EMAIL_APD=os.getenv("COA_FORMS_EMAIL_APD")
    EMAIL_OPO_REPLYTO=os.getenv("COA_FORMS_EMAIL_REPLYTO")

S3_KEY                    = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET                 = os.getenv("AWS_SECRET_ACCESS_KEY")
DEFALUT_REGION            = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_LOCATION               = f'http://{S3_UPLOADS_BUCKET}.s3.amazonaws.com/'
