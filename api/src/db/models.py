# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import relationship

from src.db.base import Base
from src.db.custom import AwareDateTime


class Timezone(Base):
    __tablename__ = 'timezones'

    name = Column(String(256), primary_key=True, index=True)


class Hike(Base):
    __tablename__ = 'hikes'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    start = Column(AwareDateTime)
    end = Column(AwareDateTime)
    zone = Column(Text, ForeignKey(Timezone.name), nullable=True, server_default='UTC')
    title = Column(Text)
    brief = Column(Text)
    description = Column(Text)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'name': self.name,
            'start': self.start,
            'end': self.end,
            'zone': self.zone,
            'title': self.title,
            'brief': self.brief,
            'description': self.description,
        }
        return ret


class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Hike.id, ondelete='CASCADE'), nullable=False)

    name = Column(Text)
    description = Column(Text)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'parent': self.parent,
            'name': self.name,
            'description': self.description,
        }
        return ret


class TrackSegment(Base):
    __tablename__ = 'tracksegments'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Track.id, ondelete='CASCADE'), nullable=False)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'parent': self.parent,
        }
        return ret


class TrackData(Base):
    __tablename__ = 'trackdata'

    id = Column(Integer, primary_key=True)
    segment = Column(Integer, ForeignKey(TrackSegment.id, ondelete='CASCADE'), nullable=False)

    time = Column(AwareDateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)


class Waypoint(Base):
    __tablename__ = 'waypoints'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Hike.id, ondelete='CASCADE'), nullable=False)

    name = Column(Text)
    description = Column(Text)

    time = Column(AwareDateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)


class Picture(Base):
    __tablename__ = 'pictures'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Hike.id, ondelete='CASCADE'), nullable=False)

    name = Column(Text, nullable=False)
    fmt = Column(Text, nullable=False)
    time = Column(AwareDateTime, nullable=False)
    description = Column(Text)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'parent': self.parent,
            'name': self.name,
            'fmt': self.fmt,
            'time': self.time,
            'description': self.description,
        }
        return ret


class PictureData(Base):
    __tablename__ = 'picturedata'

    id = Column(Integer, primary_key=True)
    parent = Column(Integer, ForeignKey(Picture.id, ondelete='CASCADE'), nullable=False)

    size = Column(Integer, nullable=False)
    resized = Column(String(32), nullable=False)
    sha = Column(String(256), nullable=False)
    data = Column(LargeBinary(1 << 24), nullable=False)

    @property
    def serialized(self) -> dict:
        ''' Return dict for use when serializing. '''
        ret = {
            'id': self.id,
            'parent': self.parent,
            'size': self.size,
            'resized': self.resized,
            'sha': self.sha,
        }
        return ret


class ApiSession(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True)
    key = Column(String(256), unique=True, nullable=False)
    username = Column(Text, nullable=False)
    displayname = Column(Text, nullable=False)
    admin = Column(Boolean, default=False)
