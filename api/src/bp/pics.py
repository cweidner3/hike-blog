from pathlib import Path
import flask
from flask_expects_json import expects_json
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.common import GLOBALS, picture_format, picture_timestamp, strict_schema
from src.db.core import engine
from src.db.models import Picture
from src.middleware import auth_as_admin

bp_pics = flask.Blueprint('pics', __name__, url_prefix='/pictures')

bp_pics_admin = flask.Blueprint('pics', __name__)
bp_pics_admin.before_request(auth_as_admin)


UPDATE_PIC_SCHEMA = {
    'type': 'object',
    'properties': {
        'description': {'type': 'string'},
        'name': {'type': 'string'},
        'time': {'type': 'string', 'format': 'date-time'},
    },
    'required': [],
}


####################################################################################################
# Read Only Routes

@bp_pics.get('')
def list_pics():
    ''' Return list of pictures. '''
    with Session(engine) as session:
        if flask.request.method == 'GET':
            count = session.execute(
                select(func.count(Picture.id))
            ).one()
            GLOBALS.logger.debug('Count res: %s', count)
            count = count[0]
            data = session.execute(
                select(Picture)
            ).scalars()
            data = list(map(lambda x: x.json, map(flask.jsonify, data)))
            return {'metadata': {'total': count}, 'data': data}
        raise ValueError(f'Unhandled request method type "{flask.request.method}"')


@bp_pics.get('/')
def list_pics_():
    ''' Return list of tracks. '''
    return list_pics()


@bp_pics.get('/<int:pic_id>')
def get_pic(pic_id: int):
    ''' Return list of tracks. '''
    with Session(engine) as session:
        if flask.request.method == 'GET':
            pic = session.execute(
                select(Picture)
                .where(Picture.id == pic_id)
            ).scalar_one()
            return flask.jsonify(pic)
        raise ValueError(f'Unhandled request method type "{flask.request.method}"')


####################################################################################################
# Restricted Routes

@bp_pics_admin.post('/hike/<int:hike_id>')
def upload_picture(hike_id: int):
    ''' Return list of tracks. '''
    with Session(engine) as session:
        if not flask.request.files:
            raise ValueError('Must provide files for uplaoding images')
        created = []
        for filename, file in flask.request.files.items():
            file_data = file.stream.read()
            fmt = picture_format(file_data)
            ts_ = picture_timestamp(file_data)
            pic = Picture(
                name=filename,
                parent=hike_id,
                data=file_data,
                time=ts_,
                fmt=fmt,
            )
            session.add(pic)
            created.append(pic)
        session.flush()
        created = list(map(lambda x: x.json, map(flask.jsonify, created)))
        session.commit()
        return {'status': 'OK', 'created': created}


@bp_pics_admin.post('/<int:pic_id>')
@expects_json(UPDATE_PIC_SCHEMA, check_formats=True)
def picture_update_one(pic_id: int):
    ''' Update the metadata of an uploaded picture. '''
    strict_schema(UPDATE_PIC_SCHEMA)
    data = flask.request.json
    assert data is not None
    with Session(engine) as session:
        ret = session.execute(
            select(Picture)
            .where(Picture.id == pic_id)
        ).scalar_one()
        for key, value in data.items():
            if key == 'name':
                suffix = Path(ret.name).suffix
                if not value.endswith(suffix):
                    value = f'{value}{suffix}'
            setattr(ret, key, value)
        session.commit()
        return {'status': 'OK'}


####################################################################################################

bp_pics.register_blueprint(bp_pics_admin)
