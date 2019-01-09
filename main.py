# Flask
from flask import Flask, flash, request, render_template, \
                    redirect, url_for, send_from_directory, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# File Management
import os, io, base64, boto3, datetime, time, calendar, requests
from PIL import Image
from botocore.exceptions import ClientError

# Random hash generation
import uuid, hashlib, hmac, re

# Knack integrator
import knackpy, json



















#  dP""b8  dP"Yb  88b 88 888888 88  dP""b8
# dP   `" dP   Yb 88Yb88 88__   88 dP   `"
# Yb      Yb   dP 88 Y88 88""   88 Yb  "88
#  YboodP  YbodP  88  Y8 88     88  YboodP

#
# Configuration & Environment Variables
#

UPLOAD_FOLDER = '/tmp'
DEPLOYMENT_MODE           = os.getenv("DEPLOYMENT_MODE", "LOCAL")
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

KNACK_APPLICATION_ID      = os.getenv("KNACK_APPLICATION_ID")
KNACK_API_KEY             = os.getenv("KNACK_API_KEY")
KNACK_API_ENDPOINT_FILE_UPLOADS="https://api.knack.com/v1/applications/" + KNACK_APPLICATION_ID + "/assets/file/upload"
S3_KEY                    = os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET                 = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET                 = os.getenv("AWS_BUCKET_NAME")
S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
DEFALUT_REGION            = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
LOG_TABLE                 = os.getenv("PM_LOGTABLE", "police-monitor-records")

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app) # Get rid of me!!!!
# https://github.com/corydolphin/flask-cors

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DEPLOYMENT_MODE'] = DEPLOYMENT_MODE
app.config['S3_BUCKET'] = S3_BUCKET
app.config['S3_LOCATION'] = S3_LOCATION
app.config['DEFALUT_REGION'] = DEFALUT_REGION
app.config['LOG_TABLE'] = LOG_TABLE
app.config['S3_KEY']      = S3_KEY
app.config['S3_SECRET']   = S3_SECRET

if(DEPLOYMENT_MODE == "LOCAL"):
    # Initialize S3 Client
    s3 = boto3.client("s3",region_name=DEFALUT_REGION, aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    dynamodb_client = boto3.client('dynamodb', region_name=DEFALUT_REGION, aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
    client = boto3.client('ses', region_name=DEFALUT_REGION, aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)
else:
    # We should already have access to these resources
    s3 = boto3.client("s3", region_name=DEFALUT_REGION)
    dynamodb_client = boto3.client('dynamodb', region_name=DEFALUT_REGION)
    ses_client = boto3.client('ses', region_name=DEFALUT_REGION)

# Default Email Configuration (Default structure)
emailConfigDefault = {
    "charset": "UTF-8",
    "html": "",
    "text": "Test sent from API",
    "subject": "Amazon SES Test (SDK for Python)",
    "sender": "Office of Design and Delivery <no-reply@austintexas.io>",
    "recipient": "no-reply@austintexas.io"
}





















#8  88 888888 88     88""Yb 888888 88""Yb .dP"Y8
#8  88 88__   88     88__dP 88__   88__dP `Ybo."
#88888 88""   88  .o 88"""  88""   88"Yb  o.`Y8b
#8  88 888888 88ood8 88     888888 88  Yb 8bodP'

#
# Helper Functions
#
def build_response(inputDict):
    return jsonify(inputDict), inputDict["status_code"]

def filename_timestamp():
  now = datetime.datetime.now()
  return now.strftime("%m%d%Y")

def getYyyyMmDd():
    return datetime.datetime.now().strftime('%Y%m%d')

def getCurrentDateTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def allowed_file(filename):
    return '.' in filename and \
            get_file_extension(filename) in ALLOWED_EXTENSIONS

def is_image(filename):
    return get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS

def is_json(inputText):
    try:
        json_object = json.loads(inputText)
        # The JSON is good
        return True
    except:
        # The JSON test is bad
        return False


def load_map(file_path):
    return json.load(open(file_path))

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def generate_amz_date():
    return datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

def generate_random_hash():
    rand_uuid_str = "{0}".format(uuid.uuid1()).encode()
    return hashlib.sha256(rand_uuid_str).hexdigest()

def is_valid_casenumber(case):
	pattern = re.compile("^([0-9]){4}-([0-9]){4}-([a-z0-9]){4}$")
	return str(pattern.match(case)) != "None"

def generate_casenum():
	datestr = datetime.datetime.now().strftime('%Y-%m%d-')
	rndstr = generate_random_hash()[0:4]
	return "{0}{1}".format(datestr,rndstr)

def generate_random_filename(filename):
  timestamp = filename_timestamp()
  original_extension = get_file_extension(filename)
  output_hash = generate_random_hash()
  return "{0}_{1}.{2}".format(timestamp, output_hash, original_extension)

def get_knack_object(tablename):
    knack_objects = load_map('./knackmaps/knack_objects.json')
    return knack_objects[tablename]

def build_knack_item_raw(inputJson, map):
    # Copy record map, we do not want it modified
    rawRecord = map.copy()

    # Convert inputJson to string (if it isn't)
    if(isinstance(inputJson, str)):
        jsonObject = json.loads(inputJson)
    else:
        jsonObject = inputJson

    # For each key,val in jsonObject
    for key, val in jsonObject.items():
        try:
            rawRecord[key] = val
        except:
            print("Invalid Key: " + key)

    return rawRecord

def build_knack_item(inputJson, map, record):
    # Copy record map, we do not want it modified
    knackRecord = record.copy()

    # Convert inputJson to string (if it isn't)
    if(isinstance(inputJson, str)):
        jsonObject = json.loads(inputJson)
    else:
        jsonObject = inputJson

    # For each key,val in jsonObject
    for key, val in jsonObject.items():
        try:
            knackRecord[map[key]] = val
        except:
            print("Invalid Key: " + key)

    return knackRecord

def knack_create_record(record, table='complaints'):
    response = knackpy.record(
        record,
        obj_key = get_knack_object(table),
        app_id  = KNACK_APPLICATION_ID,
        api_key = KNACK_API_KEY,
        method='create'
    )

    return response["id"], response




def get_dynamodb_record(identifierHash):
    print("get_dynamodb_record() Record: " + identifierHash)
    dynamodb_response = dynamodb_client.get_item(
        TableName=LOG_TABLE,
        Key={
            'entryId': { 'S': str(identifierHash) }
        }
    )

    item = dynamodb_response.get('Item')

    if not item:
        return None

    return jsonify({
        'entryId': item.get('entryId').get('S'),
        'timestamp': item.get('timestamp').get('N'),
        'type': item.get('type').get('S'),
        'data': item.get('data').get('S')
    })


def create_dynamodb_record(inputJson, type='record', case_number="", knack_record_id=''):
    if(isinstance(inputJson, str) == False):
        jsonString = json.dumps(inputJson)
    else:
        jsonString = inputJson

    identifierHash = ""

    if(case_number == ""):
        identifierHash = generate_random_hash()
    else:
        identifierHash = case_number

    if(knack_record_id == ""):
        knack_record_id = generate_random_hash()

    #random_hash = generate_random_hash()
    resp = dynamodb_client.put_item(
        TableName=LOG_TABLE,
        Item={
            'entryId': {'S': identifierHash },
            'timestamp': {'N': str(int(time.time())) },
            'dateCreated': {'S': getCurrentDateTime() },
            'type': {'S': type },
            'data': { 'S': jsonString },
            'knackRecordId': {'S': knack_record_id }
        }
    )
    return identifierHash, resp

def update_dynamodb_record(case_number, inputJson, type='record', knack_record_id=''):
    if(isinstance(inputJson, str) == False):
        jsonString = json.dumps(inputJson)
    else:
        jsonString = inputJson

    if(knack_record_id == ""):
        knack_record_id = generate_random_hash()

    resp = table.update_item(
        TableName=LOG_TABLE,
        Key={
            'entryId': 'identifierHash'
        },
        UpdateExpression="set data = :d, dateCreated=:c, knackRecordId = :k",
        ExpressionAttributeValues={
            ':d': jsonString,
            ':c': getCurrentDateTime(),
            ':k': knack_record_id
        },
        ReturnValues="UPDATED_NEW"
    )

    return identifierHash, resp

def knack_upload_image(filepath):
    # First try uploading the image and parse the response
    try:
        headers = {'x-knack-rest-api-key': KNACK_API_KEY }
        multiple_files = [('files', open(filepath, 'rb'))]
        return requests.post(KNACK_API_ENDPOINT_FILE_UPLOADS, headers=headers, files=multiple_files)
    # We've failed along the way...
    except:
        print("It should have never reached this point!")
        return "error"


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
# Send Email Function
#
def sendEmail(emailConfig):
    try:
        #Provide the contents of the email.
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [
                    emailConfig['recipient'],
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': emailConfig['charset'],
                        'Data': emailConfig['html'],
                    },
                    'Text': {
                        'Charset': emailConfig['charset'],
                        'Data': emailConfig['text'],
                    },
                },
                'Subject': {
                    'Charset': emailConfig['charset'],
                    'Data': emailConfig['subject'],
                },
            },
            Source=emailConfig['sender']
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
        return "error"
    else:
        mid = response['MessageId']
        print("Email sent! Message ID: " + mid)
        return mid

#
# Routes
#

@app.route('/')
def index():
    return "Hello, world!", 200



@app.route('/form/post-debug', methods=['GET', 'POST'])
def post_debug():
    jsonStr = json.dumps(request.form)
    requestJson = json.dumps(request.json)
    print("Request.form:")
    print(jsonStr)

    print("Request.json:")
    print(requestJson)
    return jsonStr, 200



@app.route('/form/register', methods=['GET'])
def casenum_register():

    #
    # Keep generating a case number until a new record is created.
    #
    while True:
        caseNum = generate_casenum() # Generate case num.
        print("casenum_register() Case Number: " + caseNum)
        record = get_dynamodb_record(caseNum) # Record is 'None' if not found.

        if(record == None):
            print("casenum_register() Record not found, creating new...")
            caseNumResp, resp = create_dynamodb_record(inputJson='{"type": "new_form_submission_placeholder"}',case_number=caseNum)
            return jsonify({ 'status': 'success', 'case_number': caseNumResp}), 200
        else:
            print("Case number already exists: " + caseNum + ", generating a new one.")




@app.route('/form/submit', methods=['POST'])
def casenum_updaterecord():

    caseNum = "2019-0106-6370"
    record = get_dynamodb_record(caseNum)

    # if the record is found
    if(record != None):
        caseNumResp, resp = create_dynamodb_record(case_number=caseNum, inputJson='{"type": "placeholder"}')
        return jsonify({ 'status': 'success', 'case_number': caseNumResp}), 200
    else:
        return jsonify({ 'status': 'error', 'record': record}), 200




@app.route('/file/download/<path:path>', methods=['GET'])
def file_download_uri(path):

    fileUrlS3 = S3_LOCATION + path

    url = s3.generate_presigned_url(
        ExpiresIn=60, # seconds
        ClientMethod='get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': path
        }
    )

    print (url)

    return redirect(url, code=302)
    #return jsonify({"message": "Oh, yes: " + fileUrlS3}), 200












#8  dP 88b 88    db     dP""b8 88  dP     88""Yb 888888  dP""b8  dP"Yb  88""Yb 8888b.  .dP"Y8
#8odP  88Yb88   dPYb   dP   `" 88odP      88__dP 88__   dP   `" dP   Yb 88__dP  8I  Yb `Ybo."
#8"Yb  88 Y88  dP__Yb  Yb      88"Yb      88"Yb  88""   Yb      Yb   dP 88"Yb   8I  dY o.`Y8b
#8  Yb 88  Y8 dP""""Yb  YboodP 88  Yb     88  Yb 888888  YboodP  YbodP  88  Yb 8888Y"  8bodP'

@app.route('/emailtest', methods=['GET', 'POST'])
def emailtest():
    #
    # E-Mail Configuration
    #

    # Check if the method is post
    if request.method == 'POST':
        stringOutput = render_template('email.html', type='Office Of Design and Delivery', content='This is a test.')

        user_email = request.form["user_email"]
        print("User email: " + user_email)

        emailConfig = emailConfigDefault.copy()
        emailConfig['html'] = stringOutput
        emailConfig['recipient'] = user_email

        response = sendEmail(emailConfig)
        return "Output: " + response, 200

    else:
        return render_template('email_form.html', url=url_for('emailtest')), 200


@app.route('/knack/getrecord/<string:record_id>', methods=['GET'])
def get_record(record_id):
    print("Record: " + record_id)
    dynamodb_response = dynamodb_client.get_item(
        TableName=LOG_TABLE,
        Key={
            'entryId': { 'S': str(record_id) }
        }
    )

    item = dynamodb_response.get('Item')
    print(item)

    if not item:
        return jsonify({'error': 'User does not exist'}), 404

    return jsonify({
        'entryId': item.get('entryId').get('S'),
        'timestamp': item.get('timestamp').get('N'),
        'type': item.get('type').get('S'),
        'data': item.get('data').get('S')
    }), 200




@app.route('/knack/submit', methods=['POST'])
def knack_testrelationships():
    jsonInputData = None

    try:
        jsonInputData = request.get_json()
    except:
        return "Invalid JSON request", 403

    knack_officer_map = load_map("./knackmaps/knack_officer_map.json")
    knack_officer_record = load_map("./knackmaps/knack_officer_record.json")

    knack_witness_map = load_map("./knackmaps/knack_witness_map.json")
    knack_witness_record = load_map("./knackmaps/knack_witness_record.json")

    knack_evidence_map = load_map("./knackmaps/knack_evidence_map.json")
    knack_evidence_record = load_map("./knackmaps/knack_evidence_record.json")

    knack_complaint_map = load_map("./knackmaps/knack_complaint_map.json")
    knack_complaint_record = load_map("./knackmaps/knack_complaint_record.json")

    knack_compliment_map = load_map("./knackmaps/knack_compliment_map.json")
    knack_compliment_record = load_map("./knackmaps/knack_compliment_record.json")

    officersId = []
    witnessesId = []
    evidenceFileIds = []

    #
    # Response Structure
    #

    api_response = {
        "status": "error",
        "message": "",
        "httpcode": 403
    }

    jsonObject = json.loads(json_string)


    if 'type' in jsonInputData.keys():
        submissionType = jsonInputData['type']
    else:
        api_response["message"] = "No submission type specified."
        return jsonify(api_response), api_response["httpcode"]



    #
    # First create the officers' records (if any provided)
    #
    if 'officers' in jsonInputData.keys():
        for officer in jsonInputData["officers"]:
            knack_record = build_knack_item(officer, knack_officer_map, knack_officer_record)
            entry_id, response = knack_create_record(knack_record, table="officers")
            officersId.append(entry_id)
            print("New Officer creted: " +  entry_id)



    if 'witnesses' in jsonInputData.keys():
        for witness in jsonInputData["witnesses"]:
            knack_record = build_knack_item(witness, knack_witness_map, knack_witness_record)
            entry_id, response = knack_create_record(knack_record, table="witnesses")
            witnessesId.append(entry_id)
            print("New witness creted: " +  entry_id)



    #
    #  Now the evidence records
    #
    if 'evidence' in jsonInputData.keys():
    #try:
        for knackFileId in jsonInputData["evidence"]:
            new_evidence_data = knack_evidence_map.copy()
            new_evidence_data["evidenceFile"] = knackFileId
            new_evidence_data["evidenceName"] = "Knack Attachment Id: {0}".format(knackFileId)
            new_evidence_data["evidenceUploadDate"] = getCurrentDateTime()
            new_evidence_record = build_knack_item(new_evidence_data, knack_evidence_map, knack_evidence_record)
            entry_id, response = knack_create_record(new_evidence_record, table="evidence")
            evidenceFileIds.append(entry_id)
            print("New Evidence File Creted: " +  entry_id)
    # except Exception as e:
    #     print("Error while creating evidence records: " + e.message)

    #
    # We now build the full record
    #
    knack_record = build_knack_item(jsonInputData, knack_complaint_map, knack_complaint_record)

    # We begin associating officers and evidence records to the full record.
    # Get the knack key for the officers & witnesses column & assign the value to that key
    knack_record[knack_complaint_map["officers"]] = officersId
    knack_record[knack_complaint_map["witnesses"]] = witnessesId
    knack_record[knack_complaint_map["evidence"]] = evidenceFileIds

    knack_record_raw = json.dumps(jsonInputData)
    knack_record_plain = json.dumps(knack_record)

    knack_record_id, response = knack_create_record(knack_record)
    dyn_record_id, dynamodb_response = create_dynamodb_record(knack_record_raw, type='complaint', knack_record_id=knack_record_id)
    print("New Record Created! knack_record_id: {0}, dynamo_record_id: {1}".format(knack_record_id, dyn_record_id))

    response = {}
    return jsonify(response), 200



























#88888 88 88     888888     88   88 88""Yb 88      dP"Yb     db    8888b.  .dP"Y8
#8__   88 88     88__       88   88 88__dP 88     dP   Yb   dPYb    8I  Yb `Ybo."
#8""   88 88  .o 88""       Y8   8P 88"""  88  .o Yb   dP  dP__Yb   8I  dY o.`Y8b
#8     88 88ood8 888888     `YbodP' 88     88ood8  YbodP  dP""""Yb 8888Y"  8bodP'



#
# AWS Direct Upload (from browser)
#
# 1. Request Signature: /uploads/request-signature
# 2. Generate fields:   JavaScript
# 3. Upload Files   :   Direct to S3
#
@app.route('/uploads/request-signature', methods=['GET'])
def uploads_request_signature():
    filename = request.args.get('file')
    casenumber = str(request.args.get('case')).lower()

    if(str(filename) == "None" or filename == ""):
        return json.dumps({ "status": "error", "message": "file not declared"}), 403

    if(str(casenumber) == "None" or filename == ""):
        return json.dumps({ "status": "error", "message": "case number not declared"}), 403

    if(is_valid_casenumber(casenumber) == False):
        return json.dumps({ "status": "error", "message": "invalid case number: " + casenumber}), 403


    new_filename = generate_random_filename(filename)

    new_key = "uploads/" + casenumber + "/" + new_filename

    post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=new_key
    )

    response = {
        "status": "success",
        "message": "permission granted",
        "uuid": generate_random_hash(),
        "filename": filename,
        "creds": post
    }

    return json.dumps(response), 200

#
# First method: local file, then to knack api.
#

@app.route('/upload-knack-form', methods=['GET'])
def upload_file_knack():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action='/upload-knack' method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/upload-knack', methods=['GET', 'POST'])
def upload_file():

    response = {
        "status": "error",
        "status_code": 403,
        "knack-file-id": "",
        "message": "Failed to upload file."
    }

    # Check if the method is post
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            response["message"] = "No file part"
            return build_response(response)

        # Gather file from request
        file = request.files['file']

        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            response["message"] = "No selected file"
            return build_response(response)

        # If the file has a permitted extension
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            new_filename = generate_random_filename(filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

            # We are going to try to save the file first, then upload to knack
            try:
                file.save(file_path)
                r = knack_upload_image(file_path)

                # If the response is a JSON file, then we are OK
                if(is_json(r.text)):
                    file_record = r.json()
                    response["status"] = "success"
                    response["status_code"] = 200
                    response["knack-file-record"] = file_record["id"]
                    response["message"] = file_record["public_url"]
                    dyn_rid, dyn_resp = create_dynamodb_record(json.dumps(response), type='attachment', knack_record_id=file_record["id"])
                    print("New Image uploaded: " + file_record["id"])
                else:
                    print("We have a problem: " + r.text)
                    response["message"] = "Error: " + r.text


            except Exception as e:
                response["message"] = "Error while uploading: " + str(e)

            return build_response(response)

    # Not a POST request, redirect to form
    else:
        response["message"] = "Not a POST request"

    return build_response(response)

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
