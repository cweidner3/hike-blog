from datetime import datetime
from typing import Any, Tuple

import flask
from flask_expects_json import expects_json
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.common import GLOBALS
from src.db.core import engine
from src.db.models import Hike
from src.importers import gpx

bp_hikes = flask.Blueprint('hikes', __name__, url_prefix='/hikes')

NEW_HIKE_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string'},
        'start': {'type': 'string', 'format': 'date-time'},
        'end': {'type': 'string', 'format': 'date-time'},
    },
    'required': ['name'],
}


@bp_hikes.route('/new', methods=['POST'])
@expects_json(NEW_HIKE_SCHEMA, check_formats=True)
def new_hike():
    def _conv(item: Tuple[str, Any]) -> Tuple[str, Any]:
        key, value = item
        if key in ('start', 'end'):
            value = datetime.fromisoformat(value)
        return key, value
    with Session(engine) as session:
        data = dict(map(_conv, flask.g.data.items()))
        hike = Hike(**data)
        session.add(hike)
        session.flush()
        GLOBALS.logger.debug('Hike created: %s', hike)
        session.commit()
        hike = hike.serialized
        GLOBALS.logger.debug('Hike created (serialized): %s', hike)
    return hike


@bp_hikes.route('/<int:hike_id>', methods=['DELETE'])
def delete_hike(hike_id: int):
    with Session(engine) as session:
        session.execute(
            delete(Hike)
            .where(Hike.id == hike_id)
        )
        session.commit()
    return {'status': 'OK'}


@bp_hikes.route('/<int:hike_id>/data', methods=['POST'])
def import_data(hike_id: int):
    with Session(engine) as session:
        hike = session.execute(
            select(Hike)
            .where(Hike.id == hike_id)
        ).scalar_one()
        files = flask.request.files.keys()
        GLOBALS.logger.debug('Files: %s', files)
        for file in files:
            data = gpx.import_file(flask.request.files[file].stream.read())
            GLOBALS.logger.debug('Got import data: %s', data)
    return {'status': 'OK'}
