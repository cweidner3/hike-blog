import { Outlet } from 'react-router-dom';

import Navbar from '../Navbar.jsx';
import VersionData from '../meta/version.json';

function Layout(props = {}) {
    return (
        <>
        <div className='container'>
            <Navbar />
            <Outlet />
        </div>
        <footer className='footer has-background-dark'>
            <div className='level'>
                <p className='level-item'>App Version: {VersionData.version}</p>
            </div>
        </footer>
        </>
    );
}

export default Layout;
