import { useEffect, useState } from 'react';

import { redirect } from 'react-router-dom';


import { apiCall } from '../util/fetch';

async function queryHikes() {
    const resp = apiCall('/hikes/', 'GET', { json: true });
    return resp;
}
function HikesBrowser(props = {}) {

    const [hikes, setHikes] = useState([]);


    const onItemClick = (h) => {
        console.debug('Item click', h.id);
        window.location.pathname = `/hike/${h.id}`;
    };

    useEffect(() => {
        queryHikes().then((resp) => {
            setHikes(resp.data)
        })
    }, [])

    const tbody = (hikes).map((h, i) => (
        <tr key={`hike-item-${i}`}>
            <td onClick={() => onItemClick(h)}>
                <p className='has-text-weight-bold'>{h.name}</p>
            </td>
        </tr>
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
