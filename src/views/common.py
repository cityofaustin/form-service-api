from flask import Blueprint, request, redirect
import json

from services.s3 import s3
from services.helpers import generate_clean_filename, generate_random_hash
from env import *

bp = Blueprint('common', __name__)

@bp.route('/uploads/request-signature', methods=('GET',))
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

# Used in email templates.
# Creates link to download attachments sent by form
@bp.route('/file/download/<path:path>', methods=['GET'])
def file_download_uri(path):
    url = s3.generate_presigned_url(
        ExpiresIn=60, # seconds
        ClientMethod='get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': path
        }
    )

    return redirect(url, code=302)
