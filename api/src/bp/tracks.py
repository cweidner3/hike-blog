import flask
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.core import engine
from src.db.models import Track, TrackData, TrackSegment

bp_tracks = flask.Blueprint('tracks', __name__, url_prefix='/tracks')


@bp_tracks.route('', methods=['GET'])
def list_tracks():
    ''' Return list of tracks. '''
    with Session(engine) as session:
        tracks = session.execute(
            select(Track)
        ).scalars()
        tracks = list(map(lambda x: x.json, map(flask.jsonify, tracks)))
        return {'data': tracks}


@bp_tracks.route('/', methods=['GET'])
def list_tracks_():
    ''' Return list of tracks. '''
    return list_tracks()


@bp_tracks.route('/<int:track_id>', methods=['GET'])
def one_track(track_id: int):
    ''' Manage a track instance. '''
    with Session(engine) as session:
        if flask.request.method == 'GET':
            track = session.execute(
                select(Track)
                .where(Track.id == track_id)
            ).scalar_one()
            return flask.jsonify(track)
    raise ValueError(f'Unhandled request method type "{flask.request.method}"')


@bp_tracks.route('/<int:track_id>/segment', methods=['GET'])
def list_segments(track_id: int):
    ''' List segments associated with track. '''
    with Session(engine) as session:
        track = session.execute(
            select(TrackSegment)
            .where(TrackSegment.parent == track_id)
        ).scalar_one()
        return flask.jsonify(track)


@bp_tracks.route('/<int:track_id>/segment/<int:segment_id>/points', methods=['GET'])
def list_track_points(track_id: int, segment_id: int):
    ''' List segments associated with track. '''
    with Session(engine) as session:
        points = session.execute(
            select(TrackData)
            .where(TrackData.segment == segment_id)
            .order_by(TrackData.time)
        ).scalars().all()
        return points
