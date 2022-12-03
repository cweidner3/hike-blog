import iconCamera from '../icons/faCamera.png';
import iconLocationDot from '../icons/faLocationDot.png';
import iconMapPin from '../icons/faMapPin.png';

export const ATLANTA_COORDS = [33.7675738, -84.5602143, 5];

export const TRACK_COLORS = [
    '#000088',
    '#003388',
    '#AA0088',
    '#00AA88',
    '#FF0000',
];

export const COLOR_MAP = {
    default: '#000000',
    camera: '#905000',
    waypoint: '#AA0088',
    poi: '#AAAAAA',
};

export const ICONS = {
    camera: iconCamera,
    waypoint: iconLocationDot,
    poi: iconMapPin,
};

export const MAP_SOURCES = {
    'tracks': {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: [],
        }
    },
    'waypoints': {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: [],
        },
        cluster: true,
        clusterMaxZoom: 14,
        clusterRadius: 50,
    },
    'picture': {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: [],
        }
    },
};

export const MAP_LAYERS = [
    {
        id: 'tracks',
        type: 'line',
        source: 'tracks',
        paint: {
            'line-color': ['get', 'color'],
            'line-opacity': 1,
            'line-width': 3,
        },
    },
    {
        id: 'waypoints-clustered',
        filter: ['has', 'point_count'],
        type: 'circle',
        source: 'waypoints',
        layout: {},
        paint: {
            'circle-color': COLOR_MAP.circle ?? '#FFF',
            'circle-radius': 15,
            'circle-stroke-width': 1,
        },
    },
    {
        id: 'waypoints-clustered-labels',
        filter: ['has', 'point_count'],
        type: 'symbol',
        source: 'waypoints',
        layout: {
            'text-field': ['get', 'point_count_abbreviated'],
            'text-size': 12,
        },
        paint: {},
    },
    {
        id: 'waypoints',
        filter: ['!', ['has', 'point_count']],
        type: 'symbol',
        source: 'waypoints',
        layout: {
            'icon-image': 'waypoint',
            'icon-size': 0.05,
            'icon-anchor': 'bottom',
            'icon-ignore-placement': true,
            'text-allow-overlap': true,
            'text-ignore-placement': true,
        },
        paint: {
            'icon-color': COLOR_MAP.waypoint,
        },
    },
    {
        id: 'picture',
        type: 'symbol',
        source: 'picture',
        layout: {
            'icon-image': 'camera',
            'icon-size': 0.05,
            'icon-anchor': 'bottom',
        },
        paint: {
            'icon-image': COLOR_MAP.camera ?? COLOR_MAP['default'],
        },
    },
];


/* Setup Waypoints */

/* Setup Picture Icon */
