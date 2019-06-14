import os

#####
# Environment Variables
#####
DEPLOYMENT_MODE           = os.getenv("DEPLOYMENT_MODE", "LOCAL")
AVAILABLE_LANGUAGES       = ['en', 'es']
AVAILABLE_TYPES           = ['thanks', 'complaint']
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

S3_KEY                    = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET                 = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET                 = os.getenv("AWS_BUCKET_NAME")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
DEFALUT_REGION            = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
LOG_TABLE                 = os.getenv("PM_LOGTABLE", "police-monitor-records")

EMAIL_ADDRESS_OPO         = os.getenv("EMAIL_ADDRESS_OPO")
EMAIL_ADDRESS_APD         = os.getenv("EMAIL_ADDRESS_APD")
EMAIL_ADDRESS_SENDER      = os.getenv("EMAIL_ADDRESS_SENDER")
EMAIL_ADDRESS_REPLYTO     = os.getenv("EMAIL_ADDRESS_REPLYTO")

TRANSLATION_DICT          = {
    "___default_language___": "en",
    "___default_section___": ""
}
