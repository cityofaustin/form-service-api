import os, pprint, re
from flask import Blueprint, request

from services.res_handlers import handle_email_success, handle_email_failure
from services.email import send_email
from services.dynamodb import create_dynamodb_item

bp = Blueprint('day_labor', __name__)

# If description starts with "DEBUG" or "debug", then the submission is a smoke test.
# Day Labor emails will be sent to smoke test email address
def is_smoke_test(data):
    return re.match("^DEBUG", data['jobInformation']['description'], re.IGNORECASE)

@bp.route('/', methods=('GET',))
def index():
    return "Hello, its day labor day!", 200

@bp.route('/submit', methods=('POST',))
def submit():
    data = request.json
    language_code = data["language"]
    form_type = data["type"]
    email_source = os.getenv("EMAIL_DAY_LABOR_REPLYTO")

    confirmation_number = create_dynamodb_item(form_type)

    # Handle user email
    try:
        user_email = data['employerInformation']['email']
    except:
        user_email = None

    try:
        email_recipient=os.getenv("EMAIL_DAY_LABOR")

        if (is_smoke_test(data)):
            print("Smoke Test Data")
            pprint.pprint(data)
            email_recipient=os.getenv("EMAIL_SMOKE_TEST")

        # Send email to Day Labor Department
        send_email(form_type, "en", email_recipient, email_source, confirmation_number, data)

        if (user_email):
            send_email(form_type, language_code, user_email, email_source, confirmation_number, data)
        # TODO, send an email to day labor office, not just the confirmation email.
    except Exception as e:
        return handle_email_failure(e, confirmation_number)
    else:
        return handle_email_success(confirmation_number)
