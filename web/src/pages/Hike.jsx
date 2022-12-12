import {useEffect, useRef, useState} from "react";
import {useParams} from "react-router-dom";
import ReactMarkdown from 'react-markdown';

import mapboxgl from 'mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax

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

let gHikeTimezone = 'UTC';

async function queryHike(hikeId, { includeTrack=false } = {}) {
    const query = { includeTrack };
    return apiCall(`/hikes/${hikeId}`, 'GET', { json: true, query });
}

async function queryTracks(hikeId) {
    return apiCall(`/tracks/hike/${hikeId}`, 'GET', { json: true });
}

async function queryWaypoints(hikeId) {
    return apiCall(`/hikes/${hikeId}/waypoints`, 'GET', { json: true });
}

async function queryPictures(hikeId) {
    return apiCall(`/pictures/hike/${hikeId}`, 'GET', { json: true });
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

function toDateStr(timestr) {
    const obj = new Date(timestr);
    return obj.toLocaleString('en-US', { timeZone: gHikeTimezone || 'America/New_York' });
};

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


function PicturePopup(props = {}) {
    const {
        selectedPicture = {properties: {}, geometry: {}},
    } = props;

    const picId = selectedPicture.properties.picId;
    const fmt = selectedPicture.properties.fmt;
    const time = toDateStr(selectedPicture.properties.time);
    const description = selectedPicture.properties.description;

    const img = (
        <figure className="image">
            <img src={`/api/pictures/${picId}.${fmt}`}/>
        </figure>
    );

    return (
        <div className="content">
            <p className="has-text-weight-bold">{time}</p>
            <ReactMarkdown>{description}</ReactMarkdown>
            {img}
        </div>
    );
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
            <ReactMarkdown>{description}</ReactMarkdown>
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
    else if (type === 'picture') {
        comp = (
            <PicturePopup
                selectedPicture={selected}
            />
        );
    }

    const wpId = selected.properties.id;
    const prevWp = (wpId === 0) ? null : sourceList[wpId - 1];
    const nextWp = (wpId >= (sourceList.length - 1)) ? null : sourceList[wpId + 1];

    const comColor = 'has-background-grey-lighter';

    const pageSel = (
        <div className="pagination is-left">
            <div
                className={`pagination-previous ${comColor} ${prevWp == null ? 'is-disabled' : ''}`}
                onClick={() => (prevWp != null) ? setter([type, prevWp]) : null}
            >
                Previous
            </div>
            <div
                className={`pagination-next ${comColor} ${nextWp == null ? 'is-disabled' : ''}`}
                onClick={() => (nextWp != null) ? setter([type, nextWp]) : null}
            >
                Next
            </div>
            <div
                className={`pagination-next delete is-large ${comColor}`}
                onClick={() => setter(['', null])}
            />
        </div>
    );

    return (
        <div className="content has-background-primary p-2">
            <div className="card has-background-dark">
                <div className="card-content">
                    <div className="content">
                        <div className="tile is-ancestor">
                            <div className="tile is-parent is-vertical">
                                <div className="tile is-child">
                                    {pageSel}
                                </div>
                                <div className="tile notification is-child has-background-grey-lighter">
                                    {comp}
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
        pictures = [],
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
    const [selectedPicture, setSelectedPicture] = useState(null);
    const [popup, setPopup] = useState(null);
    const [selected, setSelected] = useState(['', null]);
    const [clusterClicked, setClusterClicked] = useState(null);

    const mapStyle = { height: '60vh' };

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
                coordinates: t.segments.map((s) => s.map((p) => ([p.longitude, p.latitude]))).flat(1),
            },
            properties: {
                color: TRACK_COLORS[ti % TRACK_COLORS.length],
                name: t.name,
                description: t.description,
            },
        }));
        setTracksGJ(tracksGJ);
    }, [tracks]);

    useEffect(() => {
        if (tracks.length === 0) {
            if (pictureGJ !== 0) {
                setPictureGJ([]);
            }
            return;
        }

        const trackData = tracks.map((t) => (
            t.segments
        )).flat(2).map((x) => (
            {...x, time: new Date(x.time)}
        ));
        console.debug('Tracks data', trackData);

        const picGJ = pictures.map((p, pi) => {
            const pictime = new Date(p.time);
            let found = trackData.find((d) => d.time > pictime);
            found = found ?? trackData[trackData.length - 1];
            return {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [found.longitude, found.latitude],
                },
                properties: {
                    ...p,
                    id: pi,
                    picId: p.id,
                    iconSize: ICON_SIZES.waypoint * (
                        (selectedPicture?.properties?.id == pi) ? 2 : 1
                    ),
                },
            };
        });
        setPictureGJ(picGJ)
    }, [pictures, tracks.length, selectedPicture?.properties?.id]);

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

            mapRef.current.on('click', 'picture', (e) => {
                console.debug('Picture clicked', JSON.parse(JSON.stringify(e.features)));
                setSelected(['picture', e.features[0]]);
            });

            mapRef.current.on('click', 'picture-clustered', (e) => {
                console.debug('Picture (clustered) clicked', JSON.parse(JSON.stringify(e.features)));
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
            return
        }
        mapRef.current.getSource('picture').setData({
            type: 'FeatureCollection',
            features: pictureGJ,
        })
    }, [pictureGJ, loaded2]);

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
        if (!mapRef.current) {
            return;
        }
        const setters = {
            'waypoint': setSelectedWaypoint,
            'picture': setSelectedPicture,
        }
        if (selected[1] == null) {
            Object.values(setters).forEach((s) => {
                s?.(null);
            })
            return;
        }
        Object.entries(setters).forEach(([k, v]) => {
            if (k === selected[0]) {
                v?.(selected[1]);
            }
            else {
                v?.(null);
            }
        });
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
                sourceList={
                    (selected[0] === 'waypoint') ? waypointsGJ
                        : (selected[0] === 'picture') ? pictureGJ
                        : []
                }
            />
        </div>
    );
}

function Hike(props = {}) {
    const params = useParams();

    const [hike, setHike] = useState(null);
    const [tracks, setTracks] = useState([]);
    const [waypoints, setWaypoints] = useState([]);
    const [pictures, setPictures] = useState([]);
    const [timeString, setTimeString] = useState('');

    console.debug('Props', props.router);

    const toDateStr = (d) => {
        const obj = new Date(d);
        return obj.toLocaleString('en-US', { timeZone: hike?.timeZone || 'America/New_York' });
    };

    useEffect(() => {
        queryHike(params.hikeId).then((ret) => {
            setHike(ret);
            if (!!ret.zone) {
                gHikeTimezone = ret.zone;
            }
        }).catch((err) => console.error('Failed to get hike info:', err));
        queryTracks(params.hikeId).then((ret) => {
            setTracks(ret.data);
        }).catch((err) => console.error('Failed to get hike track info:', err));
        queryWaypoints(params.hikeId).then((ret) => {
            setWaypoints(ret.data);
        }).catch((err) => console.error('Failed to get hike waypoint info:', err));
        queryPictures(params.hikeId).then((ret) => {
            setPictures(ret.data);
        }).catch((err) => console.error('Failed to get hike pictures info:', err));
    }, [])

    useEffect(() => {
        const startTime = (hike?.start) ? toDateStr(hike.start) : null;
        const endTime = (hike?.end) ? toDateStr(hike.end) : null;
        const timeString = (
            (!!startTime && !!endTime)
            ? `${startTime} - ${endTime}`
            : (!!startTime)
            ? startTime
            : endTime
        );
        setTimeString(timeString);
    }, [hike?.id]);


    return (
        <div className="container">
            <div className="has-text-centered">
                <h1 className="title">{(hike == null) ? '...' : hike.title ?? hike.name}</h1>
                <h2 className="title is-5">{hike?.brief}</h2>
                <p><i>({timeString})</i></p>
            </div>

            <div className="block"></div>

            <div className="card has-background-grey-light">
                <div className="card-content">
                    <ReactMarkdown>{hike?.description}</ReactMarkdown>
                </div>
            </div>

            <div className="block"></div>

            <div>
                <MapContainer
                    hike={hike}
                    tracks={tracks}
                    waypoints={waypoints}
                    pictures={pictures}
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
