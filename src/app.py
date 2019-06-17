# Flask
from flask import Flask
from flask_cors import CORS

#####
# Initialize App
#####
app = Flask(__name__)
app.config['DEBUG'] = False
CORS(app) # Get rid of me!!!!
# https://github.com/corydolphin/flask-cors

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
