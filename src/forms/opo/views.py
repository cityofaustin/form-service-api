from flask import Blueprint, request, current_app

from env import *
from helpers import generate_case_number
from services.s3 import s3
from services.send_email import send_email
from services.dynamodb import get_dynamodb_item, create_dynamodb_item

bp = Blueprint('opo', __name__)

@bp.route('/', methods=('GET',))
def index():
    return "Hello, world!", 200

@bp.route('/submit', methods=('POST',))
def submit():
    data = request.json
    language_code = data["language"]
    form_type = data["type"]

    try:
        user_confirmation_only = data["userConfirmationOnly"]
    else:
        user_confirmation_only = False

    if (user_confirmation_only):
        case_number = data["confirmationCaseNumber"]
    else:
        # Generate random case_number until a unique one is found
        # Check that case_number is not already used in dynamodb
        while True:
            case_number = generate_case_number() # Generate case num.
            item = get_dynamodb_item(case_number) # Record is 'None' if not found.
            if(!item):
                break

        # Don't send form data for OPO forms (will set "data"=None)
        # Save case_number as "id" to ensure that user confirmation/case numbers are unique
        create_dynamodb_item(case_number, form_type)

    # Handle Media Data
    try:
        media_files = json.loads(data['mediaFiles'])
    except:
        media_files = []

    # Handle Location Data
    if 'location' in data:
        dataLocationTemp = data['location']
        try:
            data['location'] = json.loads(data['location'])
        except:
            data['location'] = dataLocationTemp
    else:
        data['location'] = { "address": "", "position": {"lat": "", "lng": ""}}

    # Handle user email
    try:
        user_email = data['view:contactPreferences']['yourEmail']
    except:
        user_email = None

    # Send emails
    try:
        # If this is not a user confirmation only, then submit to OPO and/or APD
        if(user_confirmation_only == False):
            # If this is a complaint, send to OPO
            if (form_type=="complaint"):
                email_recipient=EMAIL_ADDRESS_OPO
            # If this is a thank you note, send to APD
            elif(form_type=="thanks"):
                email_recipient=EMAIL_ADDRESS_APD
            else:
                raise Exception(f"form type '{form_type}' is not valid. Should be either 'complaint' or 'thanks'.")
            send_email(form_type, "en", email_recipient, case_number, data, media_files)

        # Send the user an email, if an email was provided
        if (user_email):
            email_recipient=user_email
            send_opo_email(form_type, language_code, email_recipient, case_number, data, media_files)

        # Set successful email status
        email_status = {
            'status': 'success',
            'message': 'success',
            'case_number': case_number
        }
        return jsonify(email_status), 200

    except Exception as e:
        email_status = {
            'status': 'error',
            'message': str(e),
            'case_number': case_number
        }
        return jsonify(email_status), 500
