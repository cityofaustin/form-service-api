from flask import Blueprint

bp = Blueprint('day_labor', __name__)

@bp.route('/', methods=('GET',))
def hello():
    return "Hello, its day labor day!", 200
