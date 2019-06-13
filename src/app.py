# Flask
from flask import Flask
from flask_cors import CORS

# File Management
import os

# Debug
import pprint

#####
# Initialize App
#####
app = Flask(__name__)
CORS(app) # Get rid of me!!!!
# https://github.com/corydolphin/flask-cors

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

#####
# Add configs to app
#####
app.config['DEPLOYMENT_MODE'] = DEPLOYMENT_MODE
app.config['S3_BUCKET'] = S3_BUCKET
app.config['S3_LOCATION'] = S3_LOCATION
app.config['DEFALUT_REGION'] = DEFALUT_REGION
app.config['LOG_TABLE'] = LOG_TABLE
app.config['S3_KEY']      = S3_KEY
app.config['S3_SECRET']   = S3_SECRET
app.config['DEBUG'] = False

#####
# Register Blueprints
#####
from forms.opo.views import opo
app.register_blueprint(opo)
from forms.day_labor.views import day_labor
app.register_blueprint(day_labor)

# We only need this for local development.
if __name__ == '__main__':
    app.run()
