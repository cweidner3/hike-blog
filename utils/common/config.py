import configparser
import logging
from pathlib import Path


HERE = Path(__file__).parent.resolve()
ROOT = Path(HERE)
while not Path(ROOT, '.git').exists():
    ROOT = Path(ROOT, '..').resolve()

LOG_INIT = False


class _Config:

    FILES = [
        Path(Path.home(), '.config/hike-blog/config.ini'),
        Path(ROOT, '.hike-blog.ini'),
    ]
    DEFAULTS = {
        'default': {},
    }

    def __init__(self) -> None:
        self._conf = configparser.ConfigParser()
        self._conf.read_dict(self.DEFAULTS)
        self._conf.read(self.FILES)

    def get(self, key: str, section: str = 'DEFAULT') -> str:
        ''' Get a value. '''
        return self._conf[section][key]


CONFIG = _Config()


def get_logger() -> logging.Logger:
    global LOG_INIT

    log = logging.getLogger('script')
    if not LOG_INIT:
        log.addHandler(logging.StreamHandler())
        log.setLevel(1)
        LOG_INIT = True

    return log
