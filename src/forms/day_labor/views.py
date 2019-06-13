from flask import Blueprint, current_app

day_labor = Blueprint('day_labor', __name__)

@day_labor.route('/day', methods=('GET',))
def hello():
    return "Hello, its day labor day!", 200
