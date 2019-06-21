from flask import Blueprint, request
import json, pprint

import env
from services.res_handlers import handle_email_success, handle_email_failure
from services.email import send_email
from services.dynamodb import get_dynamodb_item, create_dynamodb_item
from services.helpers import is_smoke_test

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
    except:
        user_confirmation_only = False

    if (user_confirmation_only):
        case_number = data["confirmationCaseNumber"]
    else:
        # Don't send form data for OPO forms (will set "data"={})
        case_number = create_dynamodb_item(form_type)

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
                email_recipient=env.EMAIL_ADDRESS_OPO
            # If this is a thank you note, send to APD
            elif(form_type=="thanks"):
                email_recipient=env.EMAIL_ADDRESS_APD
            else:
                raise Exception(f"form type '{form_type}' is not valid. Should be either 'complaint' or 'thanks'.")

            if (is_smoke_test(data)):
                print("Smoke Test")
                pprint.pprint(data)
                email_recipient=env.EMAIL_ADDRESS_SMOKE_TEST

            send_email(form_type, "en", email_recipient, case_number, data, media_files)

        # Send the user an email, if an email was provided
        if (user_email):
            email_recipient=user_email
            send_email(form_type, language_code, email_recipient, case_number, data, media_files)
    except Exception as e:
        return handle_email_failure(e, case_number)
    else:
        return handle_email_success(case_number)
