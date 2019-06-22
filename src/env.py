import os

#####
# Environment Variables
#####
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "local")

if (DEPLOYMENT_MODE == "production"):
    # Common
    S3_UPLOADS_BUCKET=os.getenv("COA_FORMS_PROD_S3_UPLOADS_BUCKET")
    DYNAMO_DB_TABLE="coa-forms-prod"
    EMAIL_SMOKE_TEST=os.getenv("COA_FORMS_PROD_EMAIL_SMOKE_TEST")
    # OPO
    EMAIL_OPO=os.getenv("COA_FORMS_PROD_EMAIL_OPO")
    EMAIL_APD=os.getenv("COA_FORMS_PROD_EMAIL_APD")
    EMAIL_OPO_REPLYTO=os.getenv("COA_FORMS_PROD_EMAIL_REPLYTO")
elif (DEPLOYMENT_MODE == "staging"):
    # Common
    DYNAMO_DB_TABLE="coa-forms-dev"
    S3_UPLOADS_BUCKET=os.getenv("COA_FORMS_STAGING_S3_UPLOADS_BUCKET")
    EMAIL_SMOKE_TEST=os.getenv("COA_FORMS_STAGING_EMAIL_SMOKE_TEST")
    # OPO
    EMAIL_OPO=os.getenv("COA_FORMS_STAGING_EMAIL_OPO")
    EMAIL_APD=os.getenv("COA_FORMS_STAGING_EMAIL_APD")
    EMAIL_OPO_REPLYTO=os.getenv("COA_FORMS_STAGING_EMAIL_REPLYTO")
elif (DEPLOYMENT_MODE == "dev"):
    # Common
    DYNAMO_DB_TABLE="coa-forms-dev"
    S3_UPLOADS_BUCKET="coa-forms-uploads-pr"
    EMAIL_SMOKE_TEST=os.getenv("COA_FORMS_STAGING_EMAIL_SMOKE_TEST")
    # OPO
    EMAIL_OPO=os.getenv("COA_FORMS_STAGING_EMAIL_OPO")
    EMAIL_APD=os.getenv("COA_FORMS_STAGING_EMAIL_APD")
    EMAIL_OPO_REPLYTO=os.getenv("COA_FORMS_STAGING_EMAIL_REPLYTO")
elif (DEPLOYMENT_MODE == "local"):
    # Common
    DYNAMO_DB_TABLE=os.getenv("COA_FORMS_LOCAL_DYNAMO_DB_TABLE")
    S3_UPLOADS_BUCKET=os.getenv("COA_FORMS_LOCAL_S3_UPLOADS_BUCKET")
    EMAIL_SMOKE_TEST=os.getenv("COA_FORMS_LOCAL_EMAIL_SMOKE_TEST")
    # OPO
    EMAIL_OPO=os.getenv("COA_FORMS_LOCAL_EMAIL_OPO")
    EMAIL_APD=os.getenv("COA_FORMS_LOCAL_EMAIL_APD")
    EMAIL_OPO_REPLYTO=os.getenv("COA_FORMS_LOCAL_EMAIL_REPLYTO")

S3_KEY                    = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET                 = os.getenv("AWS_SECRET_ACCESS_KEY")
DEFALUT_REGION            = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_LOCATION               = f'http://{S3_UPLOADS_BUCKET}.s3.amazonaws.com/'
