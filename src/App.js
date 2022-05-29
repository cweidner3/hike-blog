import {useState, useEffect, useRef} from 'react';

import logo from './logo.svg';
import './App.css';

import mapboxgl from 'mapbox-gl';

const {
  MAPBOXGL_ACCESS_TOKEN = 'pk.eyJ1IjoiY3dlaWRuZXIzIiwiYSI6ImNsM29wbDU0dTBxdjkzY3V2ajk2Y2I3MXcifQ.KYe1u_UcNKFneq-d0bCU0g',
} = process.env;

mapboxgl.accessToken = MAPBOXGL_ACCESS_TOKEN

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

function MapComponent(props = {}) {
  const mapRef = useRef(null);
  const mapObjRef = useRef(null);

  const mapStyleName = useState('outdoors-v11');

  useEffect(() => {
    if (mapObjRef.current === null) {
      const map = new mapboxgl.Map( {
        container: mapRef.current,
        style: mapStyleUrl(mapStyleName),
        center: [-74.5, 40],
        zoom: 9,
      });

      mapObjRef.current = map;
    }
  }, []);

  const mapStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
  };

  return (
    <div ref={mapRef} className="map-container" style={mapStyle} />
  );
}


function App() {
  return (
    <MapComponent />
  );
}

export default App;

// vim: set sw=2 ts=2 expandtab:
