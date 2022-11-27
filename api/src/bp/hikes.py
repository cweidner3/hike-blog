from datetime import datetime
from typing import Any, List, Tuple

import flask
from flask_expects_json import expects_json
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.common import GLOBALS
from src.db.core import engine
from src.db.models import Hike, TrackData, TrackSegment, Waypoint, Track
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


####################################################################################################

def _gpx_wp_to_db(session: Session, hike_id: int, item: gpx.GpxWaypoint) -> Waypoint:
    GLOBALS.logger.debug('Waypoint: %s', item)
    wpt = Waypoint(
        parent=hike_id,
        name=item.name,
        description=item.description,
        latitude=item.coords[0],
        longitude=item.coords[1],
        elevation=item.coords[2],
    )
    session.add(wpt)
    session.flush()
    return wpt


RetTrack1 = Tuple[Track, List[TrackSegment], List[TrackData]]
RetTrack2 = Tuple[TrackSegment, List[TrackData]]


def _gpx_track_segment_to_db(session: Session, track_id: int,
                             item: gpx.GpxTrackSegment) -> RetTrack2:
    GLOBALS.logger.debug('Track Segment: %s', item)
    track_seg = TrackSegment(
        parent=track_id,
    )
    session.add(track_seg)
    session.flush()
    track_seg_id = track_seg.id
    assert isinstance(track_seg_id, int)

    data = []
    for point in item:
        # GLOBALS.logger.debug('Track Point: %s', point)
        ret_point = TrackData(
            segment=track_seg_id,
            time=point.time,
            latitude=point.coords[0],
            longitude=point.coords[1],
            elevation=point.coords[2],
        )
        data.append(ret_point)
    session.add_all(data)
    session.flush()

    return track_seg, data


def _gpx_track_to_db(session: Session, hike_id: int, item: gpx.GpxTrack) -> RetTrack1:
    GLOBALS.logger.debug('Track: %s', item)
    track = Track(
        parent=hike_id,
        name=item.name,
        description=item.description,
    )
    session.add(track)
    session.flush()
    segments = []
    data = []
    for seg in item:
        track_id = track.id
        assert isinstance(track_id, int)
        ret_seg, ret_data = _gpx_track_segment_to_db(session, track_id, seg)
        segments.append(ret_seg)
        data.extend(ret_data)
    return track, segments, data


####################################################################################################

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
        session.flush()
        assert hike.id == hike_id
        files = flask.request.files.keys()
        GLOBALS.logger.debug('Files: %s', files)
        counts = {
            'wpts': 0,
            'tracks': 0,
            'segments': 0,
            'points': 0,
        }
        for file in files:
            data = gpx.import_file(flask.request.files[file].stream.read())
            for item in data:
                if isinstance(item, gpx.GpxWaypoint):
                    _gpx_wp_to_db(session, hike_id, item)
                    counts['wpts'] += 1
                elif isinstance(item, gpx.GpxTrack):
                    _, segs, data = _gpx_track_to_db(session, hike_id, item)
                    counts['tracks'] += 1
                    counts['segments'] += len(segs)
                    counts['points'] += len(data)
                else:
                    GLOBALS.logger.warning('Unhandled GpxType: %s', type(item))
        session.commit()
        hike = flask.jsonify(hike).json
        GLOBALS.logger.warning('serialized hike: %s', hike)
    return {'status': 'OK', 'items_added': counts, 'hike': hike}
