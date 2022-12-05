'''
Main entrypoint for the flask app.
'''

import http
import traceback

from flask import Flask
import flask.logging
from flask_cors import CORS
from jsonschema import ValidationError
import werkzeug.exceptions
import werkzeug.middleware.proxy_fix

from src.bp.hikes import bp_hikes
from src.bp.pics import bp_pics
from src.bp.time import bp_time
from src.bp.tracks import bp_tracks
from src.common import GLOBALS, get_secret
from src.db.core import JsonSerializer

app = Flask(__name__)

if GLOBALS.get_env('app', 'mode') == 'production':
    app.wsgi_app = werkzeug.middleware.proxy_fix.ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1,
    )

app.debug = True
app.json_encoder = JsonSerializer
app.secret_key = GLOBALS.get_env('app', 'secretfile', 'my-definately-very-complex-secret')
CORS(app)

LOG = flask.logging.create_logger(app)


@app.route('/')
def index():
    return 'Hello World!'


@app.errorhandler(Exception)
def errorhandler(error: Exception):
    LOG.error('(%s) %s', type(error), ''.join(traceback.format_exception(error)))
    code = http.HTTPStatus.INTERNAL_SERVER_ERROR
    if isinstance(error, werkzeug.exceptions.HTTPException):
        code = http.HTTPStatus(error.code)
    if isinstance(error, ValidationError):
        code = http.HTTPStatus.BAD_REQUEST
    return {'message': str(error), 'code': code.value, 'reason': code.name}, code.value


app.register_blueprint(bp_hikes)
app.register_blueprint(bp_tracks)
app.register_blueprint(bp_pics)
app.register_blueprint(bp_time)
