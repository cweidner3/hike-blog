import {useEffect, useState} from 'react';

function setDarkMode() {
    const elem = document.querySelector('body');

    let darkMode = true;
    const matchPat = /.*(; )?darkMode=(true|false)(; )?.*/;

    if (document.cookie.search(matchPat) > -1) {
        const ret = document.cookie.match(matchPat);
        darkMode = ret[2] === 'true';
    } else {
        const exp = new Date(Date.now() + (100 * 365 * 24 * 60 * 60 * 1000));
        document.cookie = `darkMode=true; expires=${exp}; path=/`;
    }

    elem.className = (darkMode) ? 'dark' : '';

    return true;
}

function Navbar(props = {}) {
    const [isActive, setIsActive] = useState(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, [])

    useEffect(() => {
        if (mounted) {
            setDarkMode();
        }
    }, [mounted])

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
