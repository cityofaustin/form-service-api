from flask import Flask
from flask_cors import CORS

from services.res_handlers import handle_internal_server_error

#####
# Initialize App
#####
app = Flask(__name__)
app.config['DEBUG'] = False
CORS(app) # TODO: implement a more strict domain acceptance policy (e.g.: limit requests to just forms.austin.gov)
app.register_error_handler(500, handle_internal_server_error)

#####
# Register Blueprints
#####
from views.common import bp
app.register_blueprint(bp, url_prefix="/")
from views.opo import bp
app.register_blueprint(bp, url_prefix="/forms/opo")
from views.day_labor import bp
app.register_blueprint(bp, url_prefix="/forms/day_labor")

# We only need this for local development.
if __name__ == '__main__':
    app.run()
