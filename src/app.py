# Flask
from flask import Flask
from flask_cors import CORS

# Debug
import pprint

# Source environment variables
from env import *

#####
# Initialize App
#####
app = Flask(__name__)
CORS(app) # Get rid of me!!!!
# https://github.com/corydolphin/flask-cors

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
from views.common import bp
app.register_blueprint(bp, url_prefix="/")
from views.opo import bp
app.register_blueprint(bp, url_prefix="/forms/opo")
from views.day_labor import bp
app.register_blueprint(bp, url_prefix="/forms/day_labor")

# We only need this for local development.
if __name__ == '__main__':
    app.run()
