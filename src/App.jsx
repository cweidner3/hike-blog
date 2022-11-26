import {useState, useEffect, useRef} from 'react';

import './App.css';
import { parseXml, toGeoJSONTrack } from './XmlParsing';

import mapboxgl, {
  NavigationControl,
  ScaleControl,
} from 'mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax

const {
  MAPBOXGL_ACCESS_TOKEN = 'pk.eyJ1IjoiY3dlaWRuZXIzIiwiYSI6ImNsM29wbDU0dTBxdjkzY3V2ajk2Y2I3MXcifQ.KYe1u_UcNKFneq-d0bCU0g',
} = process.env;

const gPicLocation = './data/20220507-CT-North-Chick-Hike/pictures';
const gHeaderImages = [
  { name: '2022-05-07 11.11.43.jpg', alt: 'Weston Trail Head' },
  { name: '2022-05-07 11.11.57.jpg', alt: 'Cora Trail Head' },
];

mapboxgl.accessToken = MAPBOXGL_ACCESS_TOKEN

function importAll(r) {
  return r.keys().map(r);
}

const gLoadedImages = importAll(require.context('./data/20220507-CT-North-Chick-Hike/pictures/', false, /\.(png|jpe?g|svg)$/));
const gGpxData = importAll(require.context('./data/20220507-CT-North-Chick-Hike/gpx-data', false, /\.gpx$/));

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

async function loadImage(dir, image) {
  return require(`${dir}/${image}`);
}

function deconstructFilename(file) {
  const match =  file.match(/(.+)\.([a-zA-Z0-9]+)\.([a-zA-Z]+)$/);
  const filePathParts = match[1].split('/');
  return { file: file, name: filePathParts[filePathParts.length - 1], hash: match[2], ext: match[3] };
}

function transformTracks(tracks) {
  if (!tracks?.length) {
    return [];
  }
  const coords = toGeoJSONTrack(tracks[0].data.track);
  return coords;
}

function MapComponent(props = {}) {
  const {
    mapStyleName = 'outdoors-v11',
  } = props;

  const mapRef = useRef(null);
  const mapObjRef = useRef(null);

  const [tracks, setTracks] = useState([]);
  const [waypoints, setWaypoints] = useState([]);

  const [tracksGeoJSON, setTracksGeoJSON] = useState([]);

  const loadGpxData = async () => {
    const currentWp = {};
    const currentTracks = {};

    console.debug('App: Load GPX Data Started');

    const dataProm = (
      gGpxData.map(async (file, i) => {
        const fileObj = deconstructFilename(file);
        fileObj.data = await parseXml(fileObj.file);
        if (!!fileObj.data.waypoint) {
          currentWp[i] = fileObj;
        }
        if (!!fileObj.data.track) {
          currentTracks[i] = fileObj;
        }
      })
    )
    await Promise.all(dataProm).catch((err) => console.error('App: Failed to parse data:', err.message));
    console.debug('App: Tracks', currentTracks);
    setTracks(Object.values(currentTracks));
    setWaypoints(Object.values(currentWp));
  };

  useEffect(() => {
    if (mapObjRef.current == null) {
      const map = new mapboxgl.Map( {
        container: mapRef.current,
        style: mapStyleUrl(mapStyleName),
        center: [-100, 40],
        zoom: 3,
      });

      map.addControl(new ScaleControl({unit: 'imperial'}), 'bottom-right');
      map.addControl(new NavigationControl(), 'bottom-right');

      map.addSource('tracks', {
        type: 'geojson',
        data: toGeoJSONTrack([]),
      });

      map.addLayer({
        id: 'route',
        type: 'line',
        source: 'tracks',
        layout: {
          'line-join': 'round',
          'line-cap': 'round',
        },
        paint: {
          'line-color': '#00F',
          'line-opacity': 0.8,
          'line-width': 4,
        },
      });

      map.on('load', () => {
        mapObjRef.current = map;

        loadGpxData();
      });
    }
  }, []);

  useEffect(() => {
    if (mapObjRef.current == null) {
      return;
    }
    mapObjRef.current?.getSource?.('tracks')?.setData?.(
      transformTracks(tracks)
    );
  }, [tracks]);

  const mapStyle = {};

  return (
    <div ref={mapRef} className="Map" style={mapStyle} />
  );
}

function Header(props = {}) {
  const title = "Cora and Weston's Hike on the Cumberland Trail";
  const subtitle = `May 7-9, 2022: North Chickamauga Creek Segement`;

  return (<>
    <div className='hero has-text-centered'>
      <span className='title'>{title}</span>
      <span className='subtitle'>{subtitle}</span>
    </div>
  </>)
}

function TrailHeadPics(props = {}) {
  const widthFloat = 1.0 / gHeaderImages.length;
  const widthStr = `${Math.round(100 * widthFloat) - 1}%`;
  const imgStyle = {
    float: 'auto',
    width: widthStr,
    maxWidth: '400px',
    padding: '1%',
  };

  const [headImages, setHeadImages] = useState(gHeaderImages.map((x, i) => [i, x]));

  useEffect(() => {
    gHeaderImages.forEach((x, i) => {
      loadImage(gPicLocation, x.name).then((imageData) => {
        const img = headImages[i];
        img.src = imageData;
        setHeadImages({
          ...headImages,
          [i]: img,
        });
      }).catch((err) => {
        console.error(err);
      });
    });
  }, []);

  const imageTags = Object.values(headImages).map((x, i) => {
    return (!!x.src) ?
      (
        <img
          src={x.src}
          key={`${x.name ?? `trail-head-img-${i}`}`}
          style={imgStyle}
          alt={x.alt}
        />
      )
      : `${x.alt}`;
  });

  return (<>
    <div className='section has-text-centered'>
      {imageTags}
    </div>
  </>)
}

function App() {
  return (
    <div>
      <Header />
      <TrailHeadPics />
      <div className='container'>
        <div className='section'>
          <MapComponent />
        </div>
      </div>
    </div>
  );
}

export default App;

// vim: set sw=2 ts=2 expandtab:
