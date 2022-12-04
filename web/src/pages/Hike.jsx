import {useEffect, useRef, useState} from "react";
import {useParams} from "react-router-dom";
import {renderToString} from 'react-dom/server';
import ReactDOM from 'react-dom';

import mapboxgl, {
  NavigationControl,
  ScaleControl,
} from 'mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {
    faChevronLeft,
    faChevronRight,
} from '@fortawesome/free-solid-svg-icons';

import { apiCall } from "../util/fetch";
import {
    ATLANTA_COORDS,
    ICONS,
    MAP_SOURCES,
    MAP_LAYERS,
    TRACK_COLORS,
    ICON_SIZES,
} from './map-config';

const {
  MAPBOXGL_ACCESS_TOKEN = 'pk.eyJ1IjoiY3dlaWRuZXIzIiwiYSI6ImNsM29wbDU0dTBxdjkzY3V2ajk2Y2I3MXcifQ.KYe1u_UcNKFneq-d0bCU0g',
} = process.env;

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


function WaypointPopup(props = {}) {
    const {
        selectedWaypoint = {properties: {}, geometry: {}},
    } = props;

    const name = selectedWaypoint.properties.name;
    const description = selectedWaypoint.properties.description;

    const visibleCoords = [
        selectedWaypoint.properties.latitude,
        selectedWaypoint.properties.longitude,
        selectedWaypoint.properties.elevation,
    ]

    return (
        <div className="content">
            <p className="has-text-weight-bold">{name}</p>
            <p>{JSON.stringify(visibleCoords).replace(',', ', ')}</p>
            <p>{description}</p>
        </div>
    );
}

function InteractiveZone(props = {}) {
    const {
        type = '',
        selected = null,
        sourceList = [],
        setter = ([_t, _e]) => {},
    } = props;

    if (selected == null) {
        return <></>;
    }

    let comp = null;
    if (type === 'waypoint') {
        comp = (
            <WaypointPopup
                selectedWaypoint={selected}
            />
        );
    }

    const wpId = selected.properties.id;
    const prevWp = (wpId === 0) ? null : sourceList[wpId - 1];
    const nextWp = (wpId >= (sourceList.length - 1)) ? null : sourceList[wpId + 1];

    const buttonClasses = "tile is-child notification has-background-grey-lighter m-2";
    const buttonSyle = {
        height: '100%',
    }

    const leftButton = (prevWp == null) ? null : (
        <div
            className={`${buttonClasses}`}
            onClick={() => setter([type, prevWp])}
        >
            <FontAwesomeIcon icon={faChevronLeft}/>
        </div>
    );
    const closeButton = (
        <div className={`${buttonClasses}`}>
            X
        </div>
    );
    const rightButton = (nextWp == null) ? (<div className="tile is-child notification"></div>) : (
        <div
            className={buttonClasses}
            onClick={() => setter([type, nextWp])}
        >
            <FontAwesomeIcon icon={faChevronRight}/>
        </div>
    );

    return (
        <div className="content has-background-primary p-2">
            <div className="card has-background-white-ter">
                <div className="card-content">
                    <div className="content">
                        <div className="tile is-ancestor">
                            <div className="tile is-parent">
                                {leftButton}
                                <div className="tile notification is-child has-background-grey-lighter">
                                    {comp}
                                </div>
                                <div className="tile is-parent is-vertical is-1">
                                    {closeButton}
                                    {rightButton}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function MapContainer(props = {}) {
    const {
        tracks = [],
        waypoints = [],
        startingCoords = [ATLANTA_COORDS[1], ATLANTA_COORDS[0]],
        startingZoom = ATLANTA_COORDS[2],
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
    const [selectedWaypoint, setSelectedWaypoint] = useState(null);
    const [popup, setPopup] = useState(null);
    const [selected, setSelected] = useState(['', null]);
    const [clusterClicked, setClusterClicked] = useState(null);

    const mapStyle = { height: '400px'};

    useEffect(() => {
        const waypointsGJ = waypoints.map((x, xi) => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [x.longitude, x.latitude],
            },
            properties: {
                ...x,
                id: xi,
                iconSize: ICON_SIZES.waypoint * (
                    (selectedWaypoint?.properties?.id == xi) ? 2 : 1
                ),
            },
        }));
        setWaypointsGJ(waypointsGJ);
    }, [waypoints, selectedWaypoint?.properties?.id]);

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
            center: startingCoords,
            zoom: startingZoom,
        });

        mapRef.current.on('move', () => {
            setLat(mapRef.current.getCenter().lat.toFixed(4));
            setLon(mapRef.current.getCenter().lng.toFixed(4));
            setZoom(mapRef.current.getZoom().toFixed(2));
        });

        mapRef.current.on('load', () => {
            console.debug('Map loaded, adding sources and layers now...')

            Object.entries(ICONS).forEach(([name, img]) => {
                mapRef.current.loadImage(img, (error, image) => {
                    if (error) { throw error };
                    mapRef.current.addImage(name, image);
                });
            });

            Object.entries(MAP_SOURCES).forEach(([id, config]) => {
                mapRef.current.addSource(id, config);
            });

            MAP_LAYERS.forEach((layer) => {
                mapRef.current.addLayer(layer);
            })

            mapRef.current.on('click', 'waypoints', (e) => {
                console.debug('Waypoint clicked', JSON.parse(JSON.stringify(e.features)));
                setSelected(['waypoint', e.features[0]]);
            });

            mapRef.current.on('click', 'waypoints-clustered', (e) => {
                console.debug('Waypoint (clustered) clicked', JSON.parse(JSON.stringify(e.features)));
                mapRef.current.flyTo({
                    center: e.features[0].geometry.coordinates,
                    zoom: 14.5,
                })
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

        // const firstwp = waypoints[0];

        // // Ensure the map starts off focused on the hike region
        // mapRef.current.setCenter([firstwp.longitude, firstwp.latitude]);
        // mapRef.current.setZoom(7);

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

    useEffect(() => {
        if (!mapRef.current || selected[1] == null) {
            return;
        }
        if (selected[0] == 'waypoint') {
            setSelectedWaypoint(selected[1]);
        }
        mapRef.current.flyTo({
            center: selected[1].geometry.coordinates,
            zoom: 14.5,
        })
    }, [selected[1]]);

    return (
        <div>
            <div ref={mapContRef} className="Map" style={mapStyle} />

            <div className="sidebar">
                Latitude: {lat} | Longitude: {lon} | Zoom {zoom}
            </div>

            <div className="block"></div>

            <InteractiveZone
                type={selected[0]}
                selected={selected[1]}
                setter={setSelected}
                sourceList={(selected[0] === 'waypoint') ? waypointsGJ : []}
            />
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
                    startingCoords={(
                        ['longitude', 'latitude'].every((x) => !!hike && !!hike[x])
                        ? [hike?.longitude, hike?.latitude]
                        : undefined
                    )}
                    startingZoom={hike?.zoom}
                />
            </div>
        </div>
    )
}

export default Hike;
