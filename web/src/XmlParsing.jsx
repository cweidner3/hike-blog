function getName(xml) {
    return xml.querySelector('name')?.textContent
}

function getDescription(xml) {
    return xml.querySelector('desc')?.textContent
}

function getColor(xml) {
    return xml.querySelector('color')?.textContent
}

function getGpsTrack(xml) {
  const getChild = (obj, name) => {
    return obj.querySelector(name);
  }
  const queryFunc = (trkpt) => {
      return {
          timestamp: getChild(trkpt, 'time')?.textContent,
          value: [
              trkpt.getAttribute('lat'),
              trkpt.getAttribute('lon'),
              getChild(trkpt, 'ele')?.textContent,
          ],
      }
  };
  let track = xml.querySelector('trkseg');
  console.debug('trkseg', track);
  if (!track) { return null }
  const trackArr = Object.values(track.children).map(queryFunc);
  console.debug('trackArr', trackArr);
  return trackArr;
}

function getWaypoint(xml) {
    const waypoint = xml.querySelector('wpt');
    const timestamp = xml.querySelector('time');
    if (!waypoint) {
        return null;
    }
    return {
        timestamp: timestamp.textContent,
        value: [waypoint.getAttribute('lat'), waypoint.getAttribute('lon')],
    }
}

export async function parseXml(file) {
  return new Promise((resolve, reject) => {
    const rawFile = new XMLHttpRequest();
    rawFile.onreadystatechange = () => {
      if (rawFile.readyState === 4 && (rawFile.status === 200 || rawFile.status === 0)) {
        const parser = new DOMParser();
        const xml = parser.parseFromString(rawFile.response, 'text/xml');

        const data = {};
        data.name = getName(xml);
        data.description = getDescription(xml);
        data.color = getColor(xml);
        data.track = getGpsTrack(xml);
        data.waypoint = getWaypoint(xml);

        resolve(Object.fromEntries(
          Object.entries(data).filter(([_, v]) => !!v)
        ));
      }
    };

    rawFile.open('GET', file, false);
    rawFile.send();
  });
}


function toGeoJSONBase(geometry, props) {
  const feature = {};
  feature.type = 'Feature';
  feature.geometry = geometry;
  feature.properties = props;
  return {
    type: 'FeatureCollection',
    features: [feature],
  }
}

export function toGeoJSONWaypoint(item, props = {}) {
  const geo = {
    type: 'Point',
    coordinates: [item.value[1], item.value[0]],
  };
  return toGeoJSONBase(geo, props)
}

export function toGeoJSONTrack(item, props = {}) {
  const lineCoords = item.map((v) => [v.value[1], v.value[0]]);
  const geo = {
    type: 'LineString',
    coordinates: lineCoords,
  };
  return toGeoJSONBase(geo, props)
}
