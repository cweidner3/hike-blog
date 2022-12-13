import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faSpinner,
} from '@fortawesome/free-solid-svg-icons';

export default function Spinner(props = {}) {
    const {
        loading = false,
    } = props;

    const style = {width: '100%'};

    return (
        <div style={style} className='container'>
            <div hidden={!loading} style={style} className='container has-text-centered'>
                <FontAwesomeIcon icon={faSpinner} size='3x' spin />
            </div>
            <div hidden={loading} style={style} className='container'>{props.children}</div>
        </div>
    );
}
