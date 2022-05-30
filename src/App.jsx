import {useState, useEffect, useRef} from 'react';

import './App.css';

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

function MapComponent(props = {}) {
  const mapRef = useRef(null);
  const mapObjRef = useRef(null);

  const mapStyleName = useState('outdoors-v11');

  useEffect(() => {
    if (mapObjRef.current === null) {
      const map = new mapboxgl.Map( {
        container: mapRef.current,
        style: mapStyleUrl(mapStyleName),
        center: [-100, 40],
        zoom: 3,
      });

      map.addControl(new ScaleControl({unit: 'imperial'}), 'bottom-right');
      map.addControl(new NavigationControl(), 'bottom-right');

      mapObjRef.current = map;
    }
  }, []);

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

  const imageTags = Object.values(headImages).map((x) => {
    return (!!x.src) ?
      (<img src={x.src} key={`${x.name}`} style={imgStyle} alt={x.alt} />)
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
