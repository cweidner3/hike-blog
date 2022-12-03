import { Outlet } from 'react-router-dom';

import Navbar from '../Navbar.jsx';

function Layout(props = {}) {
    return (
        <div className='container'>
            <Navbar />
            <Outlet />
        </div>
    );
}

export default Layout;
