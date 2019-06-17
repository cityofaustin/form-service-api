from flask import jsonify

# Handle uncaught 500 Internal Server Errors
def handle_internal_server_error(e):
    status = {
        'status': 'error',
        'message': str(e)
    }
    return jsonify(status), 500

# Send response for a successful email sent
def handle_email_success(case_number):
    status = {
        'status': 'success',
        'message': 'success',
        'case_number': case_number
    }
    return jsonify(status), 200

# Send response for a failed email sent
def handle_email_failure(e, case_number):
    status = {
        'status': 'error',
        'message': str(e),
        'case_number': case_number
    }
    return jsonify(status), 500
