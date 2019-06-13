from flask import Blueprint, current_app

opo = Blueprint('opo', __name__)

@opo.route('/', methods=('GET',))
def index():
    return "Hello, world!", 200
