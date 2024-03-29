import itertools
import flask
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.db.core import engine
from src.db.models import Hike, Track, TrackData, TrackSegment
from src.middleware import auth_as_admin

bp_tracks = flask.Blueprint('tracks', __name__, url_prefix='/tracks')

bp_tracks_admin = flask.Blueprint('tracks', __name__)
bp_tracks_admin.before_request(auth_as_admin)


####################################################################################################
# Read Only Routes

@bp_tracks.get('')
def list_tracks():
    ''' Return list of tracks. '''
    with Session(engine) as session:
        tracks = session.execute(
            select(Track)
        ).scalars()
        tracks = list(map(lambda x: x.json, map(flask.jsonify, tracks)))
        return {'data': tracks}


@bp_tracks.get('/')
def list_tracks_():
    ''' Return list of tracks. '''
    return list_tracks()


@bp_tracks.get('/<int:track_id>')
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


@bp_tracks.get('/<int:track_id>/segment')
def list_segments(track_id: int):
    ''' List segments associated with track. '''
    with Session(engine) as session:
        track = session.execute(
            select(TrackSegment)
            .where(TrackSegment.parent == track_id)
        ).scalar_one()
        return flask.jsonify(track)


@bp_tracks.get('/<int:track_id>/segment/<int:segment_id>/points')
def list_track_points(track_id: int, segment_id: int):
    ''' List segments associated with track. '''
    with Session(engine) as session:
        points = session.execute(
            select(TrackData)
            .where(TrackData.segment == segment_id)
            .order_by(TrackData.time)
        ).scalars().all()
        return points


@bp_tracks.get('/hike/<int:hike_id>')
def tracks_from_hike(hike_id: int):
    ''' Manage a track instance. '''
    with Session(engine) as session:
        tracks = session.execute(
            select(Track)
            .where(Track.parent == hike_id)
        ).scalars()

        def _get_points(seg_id: int):
            ret = session.execute(
                select(TrackData)
                .where(TrackData.segment == seg_id)
            ).scalars()
            points = map(lambda x: x.serialized, ret)
            return list(points)

        def _get_segments(track_id: int):
            ret = session.execute(
                select(TrackSegment)
                .where(TrackSegment.parent == track_id)
            ).scalars()
            ret = map(lambda x: x.id, ret)
            segments = map(_get_points, ret)
            segments = list(segments)
            return segments

        def _format_track(track):
            ret = track.serialized
            ret['segments'] = _get_segments(track.id)
            return ret

        tracks = map(_format_track, tracks)
        tracks = list(tracks)
        return {'data': tracks}


####################################################################################################
# Restricted Routes


@bp_tracks_admin.delete('/<int:track_id>')
def track_delete_one(track_id: int):
    ''' Delete a track and allow the DB to cascade delete nested data. '''
    with Session(engine) as session:
        session.execute(
            delete(Track)
            .where(Track.id == track_id)
        )
        session.commit()
        return {'status': 'OK'}


####################################################################################################

bp_tracks.register_blueprint(bp_tracks_admin)
