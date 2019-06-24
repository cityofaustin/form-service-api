import os, json, pprint, re
from flask import Blueprint, request

from services.res_handlers import handle_email_success, handle_email_failure
from services.email import send_email
from services.dynamodb import get_dynamodb_item, create_dynamodb_item

bp = Blueprint('opo', __name__)

# If description starts with "DEBUG" or "debug", then the submission is a smoke test.
# OPO/APD emails will be sent to dev email address
def is_smoke_test(data):
    return re.match("^DEBUG", data['description'], re.IGNORECASE)

@bp.route('/', methods=('GET',))
def index():
    return "Hello, world!", 200

@bp.route('/submit', methods=('POST',))
def submit():
    print("~~~ hey we are here")
    data = request.json
    language_code = data["language"]
    form_type = data["type"]
    email_source = os.getenv("EMAIL_OPO_REPLYTO")

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

    print("~~~ about to try sending_email!")
    # Send emails
    try:
        print(f"Ist user_confirmation_only?? {user_confirmation_only}")

        # If this is not a user confirmation only, then submit to OPO and/or APD
        if(user_confirmation_only == False):
            # If this is a complaint, send to OPO
            if (form_type=="complaint"):
                email_recipient=os.getenv("EMAIL_OPO")
            # If this is a thank you note, send to APD
            elif(form_type=="thanks"):
                email_recipient=os.getenv("EMAIL_APD")
            else:
                raise Exception(f"form type '{form_type}' is not valid. Should be either 'complaint' or 'thanks'.")

            print("~~~ about to run smoke_test!")
            if (is_smoke_test(data)):
                print("Smoke Test")
                pprint.pprint(data)
                email_recipient=os.getenv("EMAIL_SMOKE_TEST")

            print(f"~~~~ yon email recipient: {email_recipient}")
            print(f"~~~~ yon email source: {email_source}")
            send_email(form_type, "en", email_recipient, email_source, case_number, data, media_files)

        # Send the user an email, if an email was provided
        if (user_email):
            email_recipient=user_email
            send_email(form_type, language_code, email_recipient, email_source, case_number, data, media_files)
    except Exception as e:
        return handle_email_failure(e, case_number)
    else:
        return handle_email_success(case_number)
