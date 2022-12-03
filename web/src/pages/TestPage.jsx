export default function TestPage(props = {}) {
    const basic = [
        '', 'white', 'light', 'dark', 'black', 'link',
    ];
    const colors = [
        'primary', 'secondary', 'info', 'success', 'warning', 'danger',
    ];

    const buttonGen = (x) => {
        const name = (!x) ? 'Button' : [x[0].toUpperCase(), x.slice(1)].join('')
        return (
            <div key={`button-${x}`} className={`button  ${(x) ? `is-${x}` : ''}`}>
                {name}
            </div>
        );
    };
    const basicButtons = basic.map(buttonGen);
    const colorButtons = colors.map(buttonGen);

    return (
        <div className="content has-text-centered">
            <div className="hero is-primary">
                <div className="hero-body">
                    <h1 className="title">Test Header</h1>
                </div>
            </div>

            <div className="block"></div>

            {basicButtons}

            <div className="block"></div>

            {colorButtons}
        </div>
    );
}
