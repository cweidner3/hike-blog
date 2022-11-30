import { Outlet } from 'react-router-dom';

import Navbar from '../Navbar.jsx';

function Layout(props = {}) {
    return (
        <>
            <Navbar />
            <Outlet />
        </>
    );
}

export default Layout;
