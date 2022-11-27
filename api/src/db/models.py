# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text, Date
from sqlalchemy.orm import relationship

from src.db.base import Base


class Hike(Base):
    __tablename__ = 'hikes'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    start = Column(Date)
    end = Column(Date)

    tracks = relationship('Track', cascade='all, delete', passive_deletes=True)
    waypoints = relationship('Waypoint', cascade='all, delete', passive_deletes=True)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'name': self.name,
            'start': self.start,
            'end': self.end,
            'tracks': list(map(lambda x: x.id, self.tracks)),
            'waypoints': list(map(lambda x: x.id, self.waypoints)),
        }
        return ret


class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Hike.id, ondelete='CASCADE'), nullable=False)

    name = Column(Text)
    description = Column(Text)

    segments = relationship('TrackSegment', cascade='all, delete', passive_deletes=True)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'parent': self.parent,
            'name': self.name,
            'description': self.description,
            'segments': list(map(lambda x: x.id, self.segments)),
        }
        return ret


class TrackSegment(Base):
    __tablename__ = 'tracksegments'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Track.id, ondelete='CASCADE'), nullable=False)

    points = relationship('TrackData', cascade='all, delete', passive_deletes=True)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'parent': self.parent,
            'points': list(map(lambda x: x.id, self.points)),
        }
        return ret


class TrackData(Base):
    __tablename__ = 'trackdata'

    id = Column(Integer, primary_key=True)
    segment = Column(Integer, ForeignKey(TrackSegment.id, ondelete='CASCADE'), nullable=False)

    time = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)


class Waypoint(Base):
    __tablename__ = 'waypoints'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Hike.id, ondelete='CASCADE'), nullable=False)

    name = Column(Text)
    description = Column(Text)

    time = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)
