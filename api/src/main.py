'''
Main entrypoint for the flask app.
'''

import http
import traceback

from flask import Flask
import flask.logging
from jsonschema import ValidationError
import werkzeug.exceptions
from flask_cors import CORS

from src.bp.hikes import bp_hikes
from src.bp.pics import bp_pics
from src.bp.tracks import bp_tracks
from src.common import get_secret
from src.db.core import JsonSerializer

app = Flask(__name__)
app.debug = True
app.json_encoder = JsonSerializer
app.secret_key = get_secret('secret-key', 'my-definately-very-complex-secret')
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
