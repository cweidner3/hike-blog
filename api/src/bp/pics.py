import flask
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.common import GLOBALS, picture_format, picture_timestamp
from src.db.core import engine
from src.db.models import Picture
from src.middleware import auth_as_admin

bp_pics = flask.Blueprint('pics', __name__, url_prefix='/pictures')

bp_pics_admin = flask.Blueprint('pics', __name__)
bp_pics_admin.before_request(auth_as_admin)


####################################################################################################
# Read Only Routes

@bp_pics.get('')
def list_pics():
    ''' Return list of tracks. '''
    with Session(engine) as session:
        if flask.request.method == 'GET':
            tracks = session.execute(
                select(func.count(Picture.id))
                .where(Picture.fmt == 'png')
            ).one()
            GLOBALS.logger.debug('Count res: %s', tracks)
            count = tracks[0]
            tracks = session.execute(
                select(Picture)
            )
            tracks = list(map(lambda x: x.json, map(flask.jsonify, tracks)))
            return {'metadata': {'total': count}, 'data': tracks}
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


####################################################################################################

bp_pics.register_blueprint(bp_pics_admin)
