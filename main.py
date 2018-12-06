# Flask
from flask import Flask, flash, request, render_template, \
                    redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename



# File Management
import os
import io
import base64
import boto3

# Random hash generation
import uuid
import hashlib

# Datetime
import datetime
import calendar

# Image Management
from PIL import Image

# Knack integrator
# by the Austin Department of Transportation
#   https://github.com/cityofaustin/knackpy
import knackpy

#
# Configuration & Environment Variables
#

UPLOAD_FOLDER = '/tmp'
DEPLOYMENT_MODE           = os.environ.get("DEPLOYMENT_MODE")
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])



KNACK_APPLICATION_ID      = os.environ.get("KNACK_APPLICATION_ID")
KNACK_API_KEY             = os.environ.get("KNACK_API_KEY")
KNACK_OBJECT_ID           = os.environ.get("KNACK_OBJECT_ID")
KNACK_API_ENDPOINT_FILE_UPLOADS="https://api.knack.com/v1/applications/${KNACK_APPLICATION_ID}/assets/file/upload"

S3_BUCKET                 = os.environ.get("AWS_BUCKET_NAME")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)


app = Flask(__name__)
CORS(app) # Get rid of me!!!!
# https://github.com/corydolphin/flask-cors

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEPLOYMENT_MODE'] = DEPLOYMENT_MODE
app.config['S3_BUCKET'] = S3_BUCKET
app.config['S3_LOCATION'] = S3_LOCATION

if(DEPLOYMENT_MODE=="local"):
    S3_KEY                    = os.environ.get("AWS_ACCESS_KEY_ID")
    S3_SECRET                 = os.environ.get("AWS_SECRET_ACCESS_KEY")
    app.config['S3_KEY']      = S3_KEY
    app.config['S3_SECRET']   = S3_SECRET
    s3 = boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
else:
    s3 = boto3.client("s3")

#
# Helper Functions
#
def filename_timestamp():
  now = datetime.datetime.now()
  return now.strftime("%m%d%Y")


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return '.' in filename and \
            get_file_extension(filename) in ALLOWED_EXTENSIONS

def knack_upload_image(filepath):
    headers = {'content-type': 'multipart/form-data', 'x-knack-rest-api-key': KNACK_API_KEY }
    files = {'file': open(filepath, 'rb')}
    r = requests.post(KNACK_API_ENDPOINT_FILE_UPLOADS, headers=headers, files=files)
    return r.text

def generate_random_filename(filename):
  timestamp = filename_timestamp()
  original_extension = get_file_extension(filename)
  rand_uuid_str = "{0}".format(uuid.uuid1()).encode()
  output_hash = hashlib.sha256(rand_uuid_str).hexdigest()
  return "{0}_{1}.{2}".format(timestamp, output_hash, original_extension)

def knack_create_record(record):
    response = knackpy.record(
        record,
        obj_key = KNACK_OBJECT_ID,
        app_id  = KNACK_APPLICATION_ID,
        api_key = KNACK_API_KEY,
        method='create'
    )

    return response


def upload_file_to_s3(file, bucket_name, acl="public-read"):

    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """
    newFilename = generate_random_filename(file.filename)

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            newFilename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(app.config["S3_LOCATION"], newFilename)



#
# Routes
#

@app.route('/')
def index():
    return "Hello, world!", 200




#
#  88  dP 88b 88    db     dP""b8 88  dP     88""Yb 888888  dP""b8  dP"Yb  88""Yb 8888b.  .dP"Y8
#  88odP  88Yb88   dPYb   dP   `" 88odP      88__dP 88__   dP   `" dP   Yb 88__dP  8I  Yb `Ybo."
#  88"Yb  88 Y88  dP__Yb  Yb      88"Yb      88"Yb  88""   Yb      Yb   dP 88"Yb   8I  dY o.`Y8b
#  88  Yb 88  Y8 dP""""Yb  YboodP 88  Yb     88  Yb 888888  YboodP  YbodP  88  Yb 8888Y"  8bodP'
#


@app.route('/knack/submit', methods=['OPTIONS', 'POST'])
def form_helper():
    print(request.get_json())
    print(jsonify(request.form))
    return jsonify(request.form)

#
# First Method: Using knackpy
#

@app.route('/knack/create_record')
def knack_record():
    record = {
        "field_2": "John Doe",
        "field_4": "theuseremail@gmail.com",
        "field_5": "Male",
        "field_6": "Dev",
        "field_7": "(777) 123-4567",
        "field_8": {
          "street": "123 Fake St.",
          "city": "Amonate",
          "state": "VA",
          "zip": "24601"
        }
    }

    response = knack_create_record(record)
    return jsonify(response), 200





#
# 888888 88 88     888888     88   88 88""Yb 88      dP"Yb     db    8888b.  .dP"Y8
# 88__   88 88     88__       88   88 88__dP 88     dP   Yb   dPYb    8I  Yb `Ybo."
# 88""   88 88  .o 88""       Y8   8P 88"""  88  .o Yb   dP  dP__Yb   8I  dY o.`Y8b
# 88     88 88ood8 888888     `YbodP' 88     88ood8  YbodP  dP""""Yb 8888Y"  8bodP'
#

#
# First method: local file, then to knack api.
#


# /tmp is guaranteed to be available during the execution of your Lambda function.
# Lambda will reuse your function when possible, and when it does,
# the content of /tmp will be preserved along with any processes
# you had running when you previously exited.
# However, the contents of /tmp (along with the memory of any running processes)
# could disappear at any time.

@app.route('/upload-knack', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads-knack/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




#
# Second Method: S3 File Uploader, then add url to knack image field.
#

@app.route("/upload-s3", methods=["GET"])
def upload_file_s3_form():
    return render_template('index.html', url=url_for('upload_file_s3')), 200

@app.route("/upload-s3", methods=["POST"])
def upload_file_s3():

	# A. Check if there
    if "user_file" not in request.files:
        return "No user_file key in request.files"

	# B. Instantiate file handle
    file    = request.files["user_file"]

    """
        These attributes are also available
        file.filename               # The actual name of the file
        file.content_type
        file.content_length
        file.mimetype
    """

	# C. Check filename is not empty
    if file.filename == "":
        return "Please select a file"

	# D. if there is a file and is allowed
    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        output   	  = upload_file_to_s3(file, app.config["S3_BUCKET"])
        return str(output), 200

    else:
        return redirect("/")


# We only need this for local development.
if __name__ == '__main__':
    app.run()
