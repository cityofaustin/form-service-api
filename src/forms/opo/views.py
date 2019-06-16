from flask import Blueprint, request, current_app

from services.s3 import s3
from env import *

bp = Blueprint('opo', __name__)

@bp.route('/', methods=('GET',))
def index():
    return "Hello, world!", 200

@bp.route('/submit', methods=['POST'])
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
        recipient = None

    #
    # Now we will attempt to send the emails
    #
    try:

        # Send the user an email
        if (recipient):
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
