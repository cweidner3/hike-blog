'''
Import GPX files. Files containing gps data in XML format. These provide all the info such as
recorded tracks and waypoints.
'''

from datetime import datetime
import functools
import operator
from typing import Iterator, List, Optional, Tuple, Union
import xml.etree.ElementTree as ET

NAMESPACE = 'http://www.topografix.com/GPX/1/1'
NS = 'gpx'

CoordsType = Tuple[Optional[float], Optional[float], Optional[float]]


class GpxElement:
    ''' Common element base class providing standardized method calls and parsing. '''

    _PROPS = [
        '_name',
        '_description',
    ]

    def __init__(self, node: Optional[ET.Element] = None,
                 props: Optional[List[str]] = None, append: bool = False) -> None:
        self._name: Optional[str] = None
        self._description: Optional[str] = None

        str_props = GpxElement._PROPS.copy() if append else []
        if props:
            str_props.extend(props)
        self._str_props = str_props

        if node:
            GpxElement._parse_node(self, node)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        it_ = self._str_props
        it_ = map(lambda x: (x, getattr(self, x)), it_)
        it_ = map(lambda x: (x[0], str(x[1])), it_)
        it_ = map("=".join, it_)
        return f'{self.__class__.__name__}[{",".join(it_)}]'

    def _parse_node(self, node: ET.Element):
        self._name = self._find_text(node, 'name')
        self._description = self._find_text(node, 'desc')

    def _get_property(self, name: str):
        value = getattr(self, name)
        assert value is not None
        return value

    def _conv_float(self, value: Optional[str]) -> Optional[float]:
        if value:
            return float(value)
        return None

    def _conv_datetime(self, value: Optional[str]) -> Optional[datetime]:
        if value:
            value = value.replace('Z', '-00:00')
            return datetime.fromisoformat(value)
        return None

    def _find(self, node: ET.Element, tag: str) -> Optional[ET.Element]:
        tag = f'{{{NAMESPACE}}}{tag}'
        for child in node:
            if child.tag == tag:
                return child
        return node.find(tag)

    def _find_text(self, node: ET.Element, tag: str) -> Optional[str]:
        tag = f'{{{NAMESPACE}}}{tag}'
        for child in node:
            if child.tag == tag:
                return child.text
        return node.findtext(tag)

    @property
    def name(self) -> Optional[str]:
        ''' Name of the element. '''
        return self._name

    @property
    def description(self) -> Optional[str]:
        ''' Description of the element, if provided. '''
        return self._description


class GpxTrackPoint(GpxElement):
    ''' Data point for a recorded track. '''

    TAG = f'{{{NAMESPACE}}}trkpt'
    _PROPS = [
        '_time',
        '_lat',
        '_lon',
        '_ele',
    ]

    def __init__(self, node: Optional[ET.Element] = None) -> None:
        self._time: Optional[datetime] = None
        self._lat: Optional[float] = None
        self._lon: Optional[float] = None
        self._ele: Optional[float] = None

        super().__init__(node=node, props=self._PROPS)
        if node:
            self._parse_node(node)

    def _parse_node(self, node: ET.Element):
        assert node.tag == self.TAG, f'Node provided, {node.tag}, is not {self.TAG}'
        self._lat = self._conv_float(node.get('lat'))
        self._lon = self._conv_float(node.get('lon'))
        ele = self._find(node, 'ele')
        if ele is not None:
            self._ele = self._conv_float(ele.text)
        time = self._find(node, 'time')
        if time is not None:
            self._time = self._conv_datetime(time.text)

    @property
    def coords(self) -> CoordsType:
        ''' Coordinates of the waypoint (lat, lon, ele). '''
        return (self._lat, self._lon, self._ele)

    @property
    def time(self) -> Optional[datetime]:
        ''' Timestamp associated with the waypoint. '''
        return self._time


class GpxTrackSegment(GpxElement):
    ''' Segment of track data. '''

    TAG = f'{{{NAMESPACE}}}trkseg'
    _PROPS = [
        'length',
    ]

    def __init__(self, node: Optional[ET.Element] = None) -> None:
        self._points: List[GpxTrackPoint] = []

        super().__init__(node=node, props=self._PROPS)
        if node:
            self._parse_node(node)

    def __iter__(self) -> Iterator[GpxTrackPoint]:
        return iter(self._points)

    def _parse_node(self, node: ET.Element):
        assert node.tag == self.TAG, f'Node provided, {node.tag}, is not {self.TAG}'
        for child in node:
            if child.tag == GpxTrackPoint.TAG:
                item = GpxTrackPoint(child)
                self._points.append(item)

    @property
    def length(self) -> int:
        ''' Total number of track points in the recorded track. '''
        return len(self._points)


class GpxTrack(GpxElement):
    ''' Recorded track data. '''

    TAG = f'{{{NAMESPACE}}}trk'
    _PROPS = [
        'segment_length',
        'length',
    ]

    def __init__(self, node: Optional[ET.Element] = None) -> None:
        self._segments: List[GpxTrackSegment] = []

        super().__init__(node=node, props=self._PROPS, append=True)
        if node:
            self._parse_node(node)

    def __iter__(self) -> Iterator[GpxTrackSegment]:
        return iter(self._segments)

    def _parse_node(self, node: ET.Element):
        assert node.tag == self.TAG, f'Node provided, {node.tag}, is not {self.TAG}'
        for child in node:
            if child.tag == GpxTrackSegment.TAG:
                item = GpxTrackSegment(child)
                self._segments.append(item)

    @property
    def segment_length(self) -> int:
        ''' Number of segments in the recorded track. '''
        return len(self._segments)

    @property
    def length(self) -> int:
        ''' Total number of track points in the recorded track. '''
        return functools.reduce(operator.add, map(lambda x: x.length, self._segments))


class GpxWaypoint(GpxElement):
    ''' Waypoint. '''

    TAG = f'{{{NAMESPACE}}}wpt'
    _PROPS = [
        '_time',
        '_lat',
        '_lon',
        '_ele',
    ]

    def __init__(self, node: Optional[ET.Element] = None) -> None:
        self._time: Optional[datetime] = None
        self._lat: Optional[float] = None
        self._lon: Optional[float] = None
        self._ele: Optional[float] = None

        super().__init__(node=node, props=self._PROPS, append=True)
        if node:
            self._parse_node(node)

    def _parse_node(self, node: ET.Element):
        assert node.tag == self.TAG, f'Node provided, {node.tag}, is not {self.TAG}'
        self._lat = self._conv_float(node.get('lat'))
        self._lon = self._conv_float(node.get('lon'))
        ele = self._find(node, 'ele')
        if ele is not None:
            self._ele = self._conv_float(ele.text)
        time = self._find(node, 'time')
        if time is not None:
            self._time = self._conv_datetime(time.text)

    @property
    def coords(self) -> CoordsType:
        ''' Get corrdinates associated with the waypoint. '''
        return (self._lat, self._lon, self._ele)

    @property
    def time(self) -> Optional[datetime]:
        ''' Get timestamp associated with the waypoint. '''
        return self._time


GpxType = Union[
    GpxElement,
    GpxWaypoint,
    GpxTrack,
    GpxTrackSegment,
    GpxTrackPoint,
]


def import_file(data: bytes) -> List[GpxType]:
    ''' Import GPX data, exported from an app like GaiaGPS. '''
    root = ET.fromstring(data.decode())
    ET.register_namespace(NS, NAMESPACE)
    ret: List[GpxType] = []
    for child in root:
        item = None
        if child.tag == GpxWaypoint.TAG:
            item = GpxWaypoint(child)
        elif child.tag == GpxTrack.TAG:
            item = GpxTrack(child)
        elif child.tag == GpxTrackSegment.TAG:
            item = GpxTrackSegment(child)
        elif child.tag == GpxTrackPoint.TAG:
            item = GpxTrackPoint(child)
        else:
            raise ValueError(f'Unhandled tag type: {child.tag}')
        if item:
            ret.append(item)
    return ret
