# Flask
from flask import Flask, flash, request, render_template, \
                    redirect, url_for, send_from_directory, jsonify

from flask_cors import CORS

# File Management
import os, io, base64, boto3, datetime, time, calendar, requests

from botocore.exceptions import ClientError

# Random hash generation
import uuid, hashlib, hmac, re

# Knack integrator
import knackpy, json, yaml

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Undefined, Template

from pprint import pprint

class SilentUndefined(Undefined):

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ''

    def _new(*args, **kwargs):
        return SilentUndefined()

    __call__ = __getitem__ = __getattr__ = _new
    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __lt__ = __le__ = \
        __gt__ = __ge__ = __int__ = __float__ = __complex__ = __pow__ = \
        __rpow__ = _fail_with_undefined_error















#  dP""b8  dP"Yb  88b 88 888888 88  dP""b8
# dP   `" dP   Yb 88Yb88 88__   88 dP   `"
# Yb      Yb   dP 88 Y88 88""   88 Yb  "88
#  YboodP  YbodP  88  Y8 88     88  YboodP

#
# Configuration & Environment Variables
#

OPO_ENV = Environment(undefined=SilentUndefined,loader=FileSystemLoader('templates'))

UPLOAD_FOLDER = '/tmp'
DEPLOYMENT_MODE           = os.getenv("DEPLOYMENT_MODE", "LOCAL")
AVAILABLE_LANGUAGES       = ['en', 'es']
AVAILABLE_TYPES           = ['thanks', 'complaint']
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

EMAIL_ADDRESS_OPO         = os.getenv("EMAIL_ADDRESS_OPO")
EMAIL_ADDRESS_APD         = os.getenv("EMAIL_ADDRESS_APD")
EMAIL_ADDRESS_SENDER      = os.getenv("EMAIL_ADDRESS_SENDER")
EMAIL_ADDRESS_REPLYTO     = os.getenv("EMAIL_ADDRESS_REPLYTO")

TRANSLATION_DICT          = {
    "___default_language___": "en",
    "___default_section___": ""
}

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
app.config['DEBUG'] = False

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

# Default Email Configuration (Default structure)
emailConfigDefault = {
    "charset": "UTF-8",
    "html": "",
    "text": "",
    "subject": "Thank You",
    "source": EMAIL_ADDRESS_SENDER, # Who sends the email
    "sender": EMAIL_ADDRESS_REPLYTO, # What it looks like in reply-to.
    "recipient": "no-reply@austintexas.io"
}








#
# TRANSLATION
#














#8  88 888888 88     88""Yb 888888 88""Yb .dP"Y8
#8  88 88__   88     88__dP 88__   88__dP `Ybo."
#88888 88""   88  .o 88"""  88""   88"Yb  o.`Y8b
#8  88 888888 88ood8 88     888888 88  Yb 8bodP'

#
# Helper Functions
#

def load_translation(file_path, section, language):
    global TRANSLATION_DICT
    with open(file_path, 'r') as stream:
        try:
            TRANSLATION_DICT = yaml.load(stream)
            TRANSLATION_DICT["___default_section___"] = section
            TRANSLATION_DICT["___default_language___"] = language
        except Exception as e:
            print(str(e))

def translate(key):
    global TRANSLATION_DICT
    section = TRANSLATION_DICT["___default_section___"]
    language = TRANSLATION_DICT["___default_language___"]

    try:
        return TRANSLATION_DICT['common'][key][language]
    except:
        """ Not found in common words, trying section """

    try:
        return TRANSLATION_DICT[section][key][language]
    except:
        print("translate() Section: '{0}', Key: '{1}', Language: '{2}' -- NOT FOUND".format(section, key, language))

    return ""

def get_language_code():
    global TRANSLATION_DICT
    try:
        return TRANSLATION_DICT["___default_language___"]
    except:
        return "en"

#
# We are going to register a custom filter, to get the file name
#
OPO_ENV.filters['basename'] = os.path.basename
OPO_ENV.globals['t'] = translate
OPO_ENV.globals['language_code'] = get_language_code


def build_response(inputDict):
    return jsonify(inputDict), inputDict["status_code"]

def filename_timestamp():
  now = datetime.datetime.now()
  return now.strftime("%m%d%Y%H%M%S")

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

def is_valid_uniqueid(uqid):
	pattern = re.compile("^([a-z0-9]){64}$")
	return str(pattern.match(uqid)) != "None"

def generate_casenum():
	datestr = datetime.datetime.now().strftime('%Y-%m%d-')
	rndstr = generate_random_hash()[0:4]
	return "{0}{1}".format(datestr,rndstr)


def get_file_name(filename):
    return filename.rsplit('.', 1)[0].lower()

def generate_random_filename(filename):
  timestamp = filename_timestamp()
  original_extension = get_file_extension(filename)
  output_hash = generate_random_hash()
  return "{0}_{1}.{2}".format(timestamp, output_hash, original_extension)

def clean_filename(filename):
	fileExt = get_file_extension(filename)
	fileName = get_file_name(filename)
	cleanFileName = re.sub(r'\W+', '', fileName)
	return "{0}.{1}".format(cleanFileName, fileExt)

def generate_clean_filename(filename):
  timestamp = filename_timestamp()
  cleanFilename = clean_filename(filename)
  shortHash = generate_random_hash()[0:5]
  return "{0}_{1}_{2}".format(timestamp, shortHash, cleanFilename)


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

# Gets the language code from the from submission:
# Use: submission_type = get_submission_type(request.json)
# submission_type contains 'thank' (example)
def get_submission_type(formJson):
    try:
        return formJson['type'] if formJson['type'] != "" else "complaint"
    except:
        return AVAILABLE_TYPES[0]

# Gets the language code from the from submission:
# Use: language_code = get_language(request.json)
# language_code contains 'en' (example)
def get_language(formJson):
    try:
        return formJson['language'] if formJson['language'] != "" else "en"
    except:
        return AVAILABLE_LANGUAGES[0]

# Returns True if the language code is supported
# Use: is_lang_supported = is_language_supported(request.json)
# is_lang_supported contains True
def is_language_supported(formJson):
    try:
        return True if get_language(formJson) in AVAILABLE_LANGUAGES else False
    except:
        return False

#
# Returns the language file as a json object
#
def load_language_file(filepath):

    isfile = os.path.isfile(filepath)

    print("load_language_file() filepath: " + filepath)
    print("load_language_file() isfile: " + str(isfile))

    try:
        with open(filepath) as data_file:
            return json.load(data_file)


    except Exception as e:
        print("load_language_file() We have an error:")
        print(e)
        return None

def render_email_template(template_filepath, **kwargs):
    template_file = os.path.basename(template_filepath)
    template = OPO_ENV.get_template(template_filepath)
    return(template.render(**kwargs))


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
        raise e
    except Exception as e:
        raise e
    else:
        mid = response['MessageId']
        print("Email sent! Message ID: " + mid)
        return mid

def is_recipient(email):
    return email not in [EMAIL_ADDRESS_OPO, EMAIL_ADDRESS_APD]

def send_opo_email(submission_type, language_code, recipient, caseNumResp, data, mediaFiles):
    # We load the language of the recipient, for opo or apd must default to english.
    currentLangCode = language_code if is_recipient(recipient) else "en"

    # load given language
    load_translation('templates/email/officepoliceoversight/language.yaml',
        section=submission_type,
        language=currentLangCode)

    # Now we specify the destination email, and translated subject
    emailConfig = None
    emailConfig = emailConfigDefault.copy()
    emailConfig['recipient'] = recipient
    emailConfig['subject'] = translate('emailSubject')

    print("~~~ About to render_email_template html")
    # Render HTML template
    htmlTemplate = render_email_template("email/officepoliceoversight/" + submission_type + "/template.html",
        casenumber=caseNumResp,
        data=data,
        attachment_urls=mediaFiles,
        api_endpoint=url_for('file_download_uri', path='', _external=True)
    )
    print("~~~ I did I did render_email_template html")

    # Render TXT template (for non-html compatible services)
    txtTemplate = render_email_template("email/officepoliceoversight/" + submission_type + "/template.txt",
        casenumber=caseNumResp,
        data=data,
        attachment_urls=mediaFiles,
        api_endpoint=url_for('file_download_uri', path='', _external=True)
    )

    emailConfig['html'] = htmlTemplate
    emailConfig['text'] = txtTemplate

    # Try to submit, capture status
    try:
        response = sendEmail(emailConfig)
    except Exception as e:
        raise e




# 88""Yb  dP"Yb  88   88 888888 888888 .dP"Y8
# 88__dP dP   Yb 88   88   88   88__   `Ybo."
# 88"Yb  Yb   dP Y8   8P   88   88""   o.`Y8b
# 88  Yb  YbodP  `YbodP'   88   888888 8bodP'

#
# Route Configuration
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

    return redirect(url, code=302)



@app.route('/uploads/request-signature', methods=['GET'])
def uploads_request_signature():
    filename = request.args.get('file')
    uniqueid = str(request.args.get('uniqueid')).lower()

    if(str(filename) == "None" or filename == ""):
        return json.dumps({ "status": "error", "message": "file not declared"}), 403

    if(str(uniqueid) == "None" or filename == ""):
        return json.dumps({ "status": "error", "message": "case number not declared"}), 403

    if(is_valid_uniqueid(uniqueid) == False):
        return json.dumps({ "status": "error", "message": "invalid unique id: " + uniqueid + " (it must be a 64-char alphanumeric hash)"}), 403


    new_filename = generate_clean_filename(filename)

    new_key = "uploads/" + uniqueid + "/" + new_filename

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






@app.route('/languagetest', methods=['POST'])
def spanish_test():
    language = get_language(request.json)
    language_supported = is_language_supported(request.json)
    response = {
        "language_supported": str(language_supported),
        "language": language
    }

    return jsonify(response), 200





@app.route('/form/submit', methods=['POST'])
def casenum_updaterecord():
    global EMAIL_ADDRESS_OPO, EMAIL_ADDRESS_APD

    caseNum = ""
    recipient = ""
    data = request.json

    requestJson = json.dumps(request.json)

    #
    # User Confirmation Only?
    #
    try:
        user_confirmation_only = data["userConfirmationOnly"]
        caseNumResp = data["confirmationCaseNumber"]
    except:
        user_confirmation_only = False
        caseNumResp = ""

    #
    # If this is not a user confirmation only, then generate a new number...
    #
    if(caseNumResp == ""):

        while True:
            caseNum = generate_casenum() # Generate case num.
            record = get_dynamodb_record(caseNum) # Record is 'None' if not found.
            if(record == None):
                break

        caseNumResp, resp = create_dynamodb_record(case_number=caseNum, inputJson='{"type": "placeholder"}')



    #
    # Submission Type
    #
    submission_type = get_submission_type(data)
    language_code = get_language(data)
    is_lang_supported = is_language_supported(data)


    #
    # Media
    #
    try:
        mediaFiles = json.loads(data['mediaFiles'])
    except:
        mediaFiles = []

    #
    # Location
    #
    if 'location' in data:
        dataLocationTemp = data['location']

        try:
            data['location'] = json.loads(data['location'])
        except:
            data['location'] = dataLocationTemp
    else:
        data['location'] = { "address": "", "position": {"lat": "", "lng": ""}}


    #
    # Our Flask Output, assume success
    #
    email_status = {
        'status': 'success',
        'message': 'success',
        'case_number': caseNumResp
    }


    #
    # We are going to try parsing the recipient
    #
    try:
        recipient = data['view:contactPreferences']['yourEmail']
    except:
        recipient = ""

    #
    # Now we will attempt to send the emails
    #
    try:

        # Send the user an email
        send_opo_email(submission_type, language_code, recipient, caseNumResp, data, mediaFiles)

        # If this is not a user confirmation only, then submit to OPO and/or APD
        if(user_confirmation_only == False):
            # Send to OPO
            send_opo_email(submission_type, language_code, EMAIL_ADDRESS_OPO, caseNumResp, data, mediaFiles)

            # If this is a thank you note, send to APD
            if(submission_type=="thanks"):
                send_opo_email(submission_type, language_code, EMAIL_ADDRESS_APD, caseNumResp, data, mediaFiles)

    except Exception as e:
        email_status = {
            'status': 'error',
            'message': str(e),
            'case_number': caseNumResp
        }

    #
    # Finally return if submission attempt presents with no errors
    #
    return jsonify(email_status), 200



@app.route('/email-template', methods=['GET'])
def emailtemplate():

    mode = request.args.get('mode')
    submission_type_override = request.args.get('type')
    language_override = request.args.get('lang')

    jsonObj = {
    	"language": "en",
    	"type": "complaint",
        "view:infoObject": {},
        "gender": "male",
        "race": "latino",
        "zipCode": "78727",
        "view:contactHeader": {},
        "willingToBeContacted": True,
        "view:contactPreferences": {
            "yourName": "John Smith",
            "yourPhone": "512-987-6543",
            "yourEmail": "john@smith.com",
            "needTranslator": True
        },
        "hasWitnessInformation": True,
        "witnesses": [
            {
                "name": "Witness #1 Name",
                "email": "witness1-email@here.com",
                "phoneNumber": "512-987-6543",
                "anythingElse": "Witness #1 Additional Details here"
            },
            {
                "name": "Witness #2 Name",
                "email": "wit2@email.com",
                "phoneNumber": "512-654-9876",
                "anythingElse": "Witness #2 Additional Details here"
            }
        ],
        "hasOfficerDetails": True,
        "officers": [
            {
                "name": "Officer #1 Name Here",
                "physicalDescription": "Officer #1 Description",
                "race": "latino",
                "gender": "male",
                "badgeNumber": "123-567",
                "uniformed": True,
                "transportation": "patrol"
            },
            {
                "name": "Officer #2 Name",
                "physicalDescription": "Officer #2 Description",
                "race": "other",
                "otherRace": "Not Sure",
                "gender": "male",
                "badgeNumber": "2272026",
                "uniformed": True,
                "transportation": "other",
                "otherTransportation": "Totally on foot"
            }
        ],
        "awareOfMedia": True,
        "mediaFiles": "[\"uploads/24f4ba858d34ee3a6fb6d3460ee64248499fd8d17d7b86997ca50c0f3c8c17f6/01312019182438_adb80_austinseal.gif\", \"uploads/24f4ba858d34ee3a6fb6d3460ee64248499fd8d17d7b86997ca50c0f3c8c17f6/01312019182438_adb80_austinseal.gif\",\"uploads/24f4ba858d34ee3a6fb6d3460ee64248499fd8d17d7b86997ca50c0f3c8c17f6/01312019182438_adb80_austinseal.gif\"]",
        "description": "This is the description of the incident.",
        "datetime": "2019-01-31 12:00",
        "hasTicket": True,
        "ticket": "7202621",
        "location": "{\"address\":\"436 W 8th St, Austin, TX 78701, United States\",\"position\":{\"lng\":-97.745934,\"lat\":30.271272}}"
    }





    #
    # ---------------------------------------------------------------
    # ---------------------------------------------------------------
    # ---------------------------------------------------------------
    #

    data = jsonObj

    #
    # Submission Type
    #
    submission_type = get_submission_type(data) if submission_type_override == None else submission_type_override

    print("Submission Type: {0}, Submission Override: {1}".format(submission_type, submission_type_override))

    language_code = get_language(data) if language_override == None else language_override
    is_lang_supported = is_language_supported(data)

    #
    # We now load the needed translation
    #
    load_translation('templates/email/officepoliceoversight/language.yaml',
        section=submission_type,
        language=language_code)



    #
    # Media Uploads
    #
    try:
    	mediaFiles = json.loads(data['mediaFiles'])
    except:
    	mediaFiles = []

    #
    # Location
    #
    if 'location' in data:
    	dataLocationTemp = data['location']

    	try:
    		data['location'] = json.loads(data['location'])
    	except:
    		data['location'] = dataLocationTemp
    else:
    	data['location'] = { "address": "", "position": {"lat": "", "lng": ""}}

    htmlTemplate = (render_email_template("email/officepoliceoversight/" + submission_type + "/template.html",
        casenumber= '2019-0208-6cff',
        data=data,
        attachment_urls=mediaFiles,
        api_endpoint=url_for('file_download_uri', path='', _external=True)
    ))

    txtTemplate = render_email_template("email/officepoliceoversight/" + submission_type + "/template.txt",
        casenumber= '2019-0208-6cff',
        data=data,
        attachment_urls=mediaFiles,
        api_endpoint=url_for('file_download_uri', path='', _external=True)
    )

    output = ""
    if(mode == "text"):
        output = txtTemplate
    else:
        output = htmlTemplate

    return output, 200


# We only need this for local development.
if __name__ == '__main__':
    app.run()
