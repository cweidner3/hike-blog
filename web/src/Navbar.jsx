import {useState} from 'react';
import { BrowserRouter, Route, Link } from 'react-router-dom';

function Navbar(props = {}) {
    const [isActive, setIsActive] = useState(false);

    return (
        <nav className='navbar is-primary'>
            <div className='navbar-brand'>
                <a className="navbar-item has-text-weight-bold" href="/">
                    Home
                </a>

                <div className="navbar-burger" onClick={() => setIsActive(!isActive)}>
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>

            <div className={`navbar-menu ${isActive ? 'is-active' : ''}`}>
                <div className="navbar-start">
                    <a className="navbar-item" href="/">
                        Home
                    </a>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
