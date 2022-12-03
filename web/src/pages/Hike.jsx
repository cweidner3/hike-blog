import {useEffect, useRef, useState} from "react";
import {useHref, useParams} from "react-router-dom";

import mapboxgl, {
  NavigationControl,
  ScaleControl,
} from 'mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax

import { apiCall } from "../util/fetch";

const {
  MAPBOXGL_ACCESS_TOKEN = 'pk.eyJ1IjoiY3dlaWRuZXIzIiwiYSI6ImNsM29wbDU0dTBxdjkzY3V2ajk2Y2I3MXcifQ.KYe1u_UcNKFneq-d0bCU0g',
} = process.env;

const ATLANTA_COORDS = [33.7675738, -84.5602143, 5];

const TRACK_COLORS = [
    '#000088',
    '#003388',
    '#AA0088',
    '#00AA88',
    '#FF0000',
];

mapboxgl.accessToken = MAPBOXGL_ACCESS_TOKEN;

async function queryHike(hikeId, { includeTrack=false } = {}) {
    const query = { includeTrack };
    return apiCall(`/hikes/${hikeId}`, 'GET', { json: true, query });
}

function mapStyleUrl(name) {
  if (name === 'outdoors') {
    return 'mapbox://styles/mapbox/outdoors-v11';
  }
  else if (name === 'satellite') {
    return 'mapbox://styles/mapbox/satellite-v9';
  }
  else if (name === 'streets') {
    return 'mapbox://styles/mapbox/streets-v11';
  }
  return 'mapbox://styles/mapbox/outdoors-v11';
}


function newPictureGJ(pictureMeta) {
    const ret = {
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [undefined, undefined],
        },
        properties: {},
    };
    if (pictureMeta == null) {
        return ret;
    }
    return ret;
}


function MapContainer(props = {}) {
    const {
        tracks = [],
        waypoints = [],
    } = props;


    const mapRef = useRef();
    const mapContRef = useRef();
    const currentStyle = mapStyleUrl();

    const [loaded, setLoaded] = useState(false);
    const [loaded2, setLoaded2] = useState(false);
    const [lat, setLat] = useState(0);
    const [lon, setLon] = useState(0);
    const [zoom, setZoom] = useState(2);
    const [waypointsGJ, setWaypointsGJ] = useState([]);
    const [tracksGJ, setTracksGJ] = useState([]);
    const [pictureGJ, setPictureGJ] = useState(newPictureGJ());

    const mapStyle = { height: '400px'};

    useEffect(() => {
        const waypointsGJ = waypoints.map((x) => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [x.longitude, x.latitude],
            },
            properties: {
                ...x,
            },
        }));
        setWaypointsGJ(waypointsGJ);
    }, [waypoints]);

    useEffect(() => {
        const tracksGJ = tracks.map((t, ti) => ({
            type: 'Feature',
            geometry: {
                type: 'LineString',
                coordinates: t.map((s) => s.map((p) => ([p.longitude, p.latitude]))).flat(1),
            },
            properties: {
                color: TRACK_COLORS[ti % TRACK_COLORS.length],
            },
        }));
        setTracksGJ(tracksGJ);
    }, [tracks]);

    useEffect(() => {
        if (mapRef.current) {
            return;
        }
        mapRef.current = new mapboxgl.Map({
            container: mapContRef.current,
            style: currentStyle,
            center: [ATLANTA_COORDS[1], ATLANTA_COORDS[0]],
            zoom: ATLANTA_COORDS[2],
        });

        mapRef.current.on('move', () => {
            setLat(mapRef.current.getCenter().lat.toFixed(4));
            setLon(mapRef.current.getCenter().lng.toFixed(4));
            setZoom(mapRef.current.getZoom().toFixed(2));
        });

        mapRef.current.on('load', () => {
            console.debug('Map loaded, adding sources and layers now...')
            /* Setup Tracks */
            mapRef.current.addSource('tracks', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: [],
                }
            });
            mapRef.current.addLayer({
                id: 'tracks',
                type: 'line',
                source: 'tracks',
                paint: {
                    'line-color': ['get', 'color'],
                    'line-opacity': 1,
                    'line-width': 3,
                },
            })

            /* Setup Waypoints */
            mapRef.current.addSource('waypoints', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: [],
                }
            });
            mapRef.current.addLayer({
                id: 'waypoints',
                type: 'symbol',
                source: 'waypoints',
                layout: {
                    'icon-image': 'harbor-15',
                },
            })

            /* Setup Picture Icon */
            mapRef.current.addSource('picture', {
                type: 'geojson',
                data: {
                    type: 'FeatureCollection',
                    features: [],
                }
            });
            mapRef.current.addLayer({
                id: 'picture',
                type: 'symbol',
                source: 'picture',
                layout: {
                    'icon-image': 'viewport-15',
                },
            })

            mapRef.current.on('click', () => {
            });

            console.debug('Done')

            setLoaded2(true);
            setLoaded(true);
        });
    }, []);

    useEffect(() => {
        // const map = new mapboxgl.Map({});
        if (!loaded2) {
            return
        }

        const firstwp = waypoints[0];

        // Ensure the map starts off focused on the hike region
        mapRef.current.setCenter([firstwp.longitude, firstwp.latitude]);
        mapRef.current.setZoom(7);

        console.debug('waypointsGJ', waypointsGJ);
        mapRef.current.getSource('waypoints').setData({
            type: 'FeatureCollection',
            features: waypointsGJ,
        })
    }, [waypointsGJ, loaded2]);

    useEffect(() => {
        if (!loaded2) {
            return;
        }

        console.debug('tracks', tracks);
        console.debug('tracksGJ', tracksGJ);
        mapRef.current.getSource('tracks').setData({
            type: 'FeatureCollection',
            features: tracksGJ,
        })
    }, [tracksGJ, loaded2]);

    return (
        <div>
            <div ref={mapContRef} className="Map" style={mapStyle} />
            <div className="sidebar">
                Latitude: {lat} | Longitude: {lon} | Zoom {zoom}
            </div>
        </div>
    );
}

function Hike(props = {}) {
    const params = useParams();

    const [hike, setHike] = useState(null);
    const [tracks, setTracks] = useState([]);
    const [waypoints, setWaypoints] = useState([]);

    console.debug('Props', props.router);

    useEffect(() => {
        queryHike(params.hikeId, {includeTrack: true}).then((ret) => {
            setTracks(ret.tracks);
            setWaypoints(ret.waypoints);
            delete ret.tracks;
            delete ret.waypoints;
            setHike(ret);
        })
    }, [])

    return (
        <div className="container">
            <div className="has-text-centered">
                <h1 className="title">{(hike == null) ? '...' : hike.name}</h1>
                <h2 className="title is-5">Brief here...</h2>
                <p><i>({hike?.start} - {hike?.end})</i></p>
            </div>

            <div className="block"></div>

            <div>
                <p>test</p>
            </div>

            <div>
                <MapContainer
                    hike={hike}
                    tracks={tracks}
                    waypoints={waypoints}
                />
            </div>
        </div>
    )
}

export default Hike;
