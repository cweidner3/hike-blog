import { useEffect, useState } from 'react';

import { apiCall } from '../util/fetch';

async function queryHikes() {
    const resp = apiCall('/hikes/', 'GET', { json: true });
    return resp;
}

function toDateStr(value, tz) {
    if (value == null) {
        return value;
    }
    const obj = new Date(value);
    return obj.toLocaleString('en-US', { timeZone: tz })
}


function HikeItem(props = {}) {
    const {
        key = `${Date.now()}`,
        hike = null,
    } = props;

    const onClick = () => {
        window.location.pathname = `/hike/${hike.id}`;
    };

    return (
        <tr key={key} className='is-hoverable'>
            <td onClick={() => onClick()}>
                <div className='level'>
                    <div className='level-left'>
                        <p className='has-text-weight-bold level-item'>
                            {hike?.title ?? hike.name}
                        </p>
                    </div>
                    <div className='level-right'>
                        <p className='level-item is-italic'>
                            {toDateStr(hike?.start) ?? toDateStr(hike?.end)}
                        </p>
                    </div>
                </div>
                <div className='is-italic'>
                    {hike?.brief}
                </div>
            </td>
        </tr>
    )
}


function HikesBrowser(props = {}) {
    const [hikes, setHikes] = useState([]);

    useEffect(() => {
        queryHikes().then((resp) => {
            setHikes(resp.data)
        })
    }, [])

    const tbody = (hikes).map((h, i) => (
        <HikeItem key={`hike-item-${i}`} hike={h} />
    ))

    return (
        <div className='container'>
            <h1 className='title has-text-centered'>
                Hikes Browser
            </h1>

            <div className='block'></div>

            <table className='table is-fullwidth is-hoverable'>
                <tbody>{tbody}</tbody>
            </table>
        </div>
    );
}

export default HikesBrowser;
