export async function apiCall(
    route,
    method,
    {
        data=null,
        json=false,
        query=null,
    } = {},
) {
    const srcIsJson = (typeof(data) !== 'string')
    const headers = {};
    headers['Content-Type'] = (srcIsJson) ? 'application/json' : 'text/plain';
    headers['Accept'] = (json) ? 'application/json' : 'text/plain';
    if (srcIsJson) {
        data = JSON.stringify(data);
    }

    let queryStr = (query != null) ? (new URLSearchParams(query)).toString() : null;
    queryStr = (queryStr != null) ? `?${queryStr}` : '';

    const url = `${window.location.origin}/api/${route.replace(/^\//, '')}${queryStr}`;

    console.debug('query at:', url);

    const resp = await fetch(url, {
        method,
        headers,
        ...((data != null) ? { data } : {}),
    });
    if (!resp.ok) {
        throw `HttpError: (${resp.status}) ${resp.statusText}`;
    }

    return json ? resp.json() : resp.text();
}

