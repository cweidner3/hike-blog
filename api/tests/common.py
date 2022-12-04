import json
import logging
from pathlib import Path
import subprocess
from typing import Optional
import urllib.parse

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.db.core import get_db_uri
from src.db.models import ApiSession

TESTS_FOLDER = Path(__file__).parent.resolve()
ROOT_FOLDER = Path(TESTS_FOLDER, '../..').resolve()
DATA_FOLDER = Path(ROOT_FOLDER, 'data').resolve()

assert all(map(lambda x: x.exists(), (TESTS_FOLDER, ROOT_FOLDER, DATA_FOLDER)))


class _Cached:
    def __init__(self) -> None:
        self._cache = {'container_ports': {}}
        self._log_init = False

    def get_published_port_addr(self, service: str, cont_port: int) -> str:
        ''' Fetches host and port and returns as origin string. '''
        cmd = 'docker-compose ps --format json'.split()
        proc = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(Path(__file__), '../..').resolve(),
        )
        data = json.loads(proc.stdout.decode())
        service_o = next(filter(lambda x: x['Service'] == service, data))
        port_o = next(
            filter(lambda x: x['TargetPort'] == cont_port, service_o['Publishers']))
        if port_o['PublishedPort'] == 0:
            host = self._get_container_ip(
                service, project=service_o['Project'])
            port = port_o['TargetPort']
        else:
            host = 'localhost'
            port = port_o['PublishedPort']
        return f'{host}:{port}'

    def _get_container_ip(self, service: str, project: str = '', index: str = '1') -> str:
        cont = '-'.join(filter(bool, [project, service, index]))
        cmd = f'docker container inspect {cont}'.split()
        proc = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(Path(__file__), '../..').resolve(),
        )
        data = json.loads(proc.stdout.decode())
        net_set = next(iter(data))['NetworkSettings']
        ip_addr = net_set['IPAddress']
        if not ip_addr:
            net_set = next(iter(net_set['Networks'].values()))
            ip_addr = net_set['IPAddress']
            assert ip_addr != ''
        return ip_addr

    def get_logger(self) -> logging.Logger:
        log = logging.getLogger('tests')
        if self._log_init is False:
            level = logging.INFO

            log.addHandler(logging.StreamHandler())

            log.setLevel(level)
            pass
        return log


_CACHED = _Cached()


def dev_url() -> str:
    ''' Get api origin string. '''
    return _CACHED.get_published_port_addr('api', 5000)


def get_db_base_url() -> str:
    ''' Get database origin string. '''
    return _CACHED.get_published_port_addr('db', 5432)


def query_route(container: str, route: str, query: Optional[dict] = None) -> str:
    if container == 'api':
        origin = dev_url()
    elif container == 'db':
        origin = get_db_base_url()
    else:
        raise ValueError(f'Unknown container {container}')
    query_str = ''
    if query:
        query_str = urllib.parse.urlencode(query)
        if query_str:
            query_str = f'?{query_str}'
    return ''.join(['http://', origin, route, query_str])


def _create_engine():
    db_url = get_db_base_url()
    _env = {
        'DB_DIALECT': 'postgres',
        'DB_USER': 'postgres',
        'DB_PASS': 'secret',
        'DB_HOST': db_url,
        'DB_NAME': 'db',
    }
    return create_engine(get_db_uri(_env))


engine = _create_engine()


def get_logger() -> logging.Logger:
    return _CACHED.get_logger()


def get_auth_key() -> str:
    ''' Get an auth key to use in restricted requests. '''
    with Session(engine) as session:
        ret = session.execute(
            select(ApiSession.key, ApiSession.admin)
            .where(ApiSession.admin == True)  # pylint: disable=singleton-comparison
            .limit(1)
        ).all()
        assert len(ret) > 0, f'Got {ret} instead'
        return ret[0][0]


if __name__ == '__main__':
    print(dev_url())
    print(get_db_base_url())
