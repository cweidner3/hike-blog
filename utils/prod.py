#!/usr/bin/env python3

import argparse
from datetime import datetime
import io
import itertools
import json
import os
from pathlib import Path
import re

from alembic import config
import alembic
import alembic.command
import pytz
import requests

from common.config import CONFIG, ROOT, get_logger

LOG = get_logger()


####################################################################################################

def _time_type(value: str) -> datetime:
    dates = ['%Y-%m-%d', '%Y/%m/%d', '%b %m %Y']
    times = ['%H', '%H:%M', '%H:%M:%S']
    fmts = itertools.product(dates, times)
    fmts, t_variant = itertools.tee(fmts)
    fmts = map(' '.join, fmts)
    t_variant = map('T'.join, t_variant)
    fmts = list(itertools.chain(fmts, t_variant))
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass
    for fmt in fmts:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise argparse.ArgumentTypeError(f'Unable to resolve {value} into a datetime')


def _tz_type(value: str) -> str:
    if value not in pytz.common_timezones:
        raise argparse.ArgumentTypeError(f'Unknown timezone string "{value}"')
    return value


####################################################################################################

def _action_migrate(args_):
    '''
    Migrate the production database. If nothing is provided, upgrade to "head" is assumed;
    otherwise, "base" can be used to completely revert the migrations, or a relative identifier can
    be use (e.g. -3  or +2).
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('rev', nargs='?', default='head')
    args = parser.parse_args(args_.others)

    up_pat = re.compile(r'(head|\+\d+)')
    down_pat = re.compile(r'(base|-\d+)')

    if up_pat.match(args.rev):
        direction = 'upgrade'
    elif down_pat.match(args.rev):
        direction = 'downgrade'
    else:
        raise ValueError(f'Unable to interpret revision "{args.rev}"')

    api_dir = Path(ROOT, 'api')

    aconf = config.Config(str(Path(api_dir, 'alembic.ini')))
    aconf.set_section_option('alembic', 'sqlalchemy.url', CONFIG.get('uri', 'database'))

    os.chdir(api_dir)
    print(f'Direction: {direction}')
    if direction == 'upgrade':
        alembic.command.upgrade(aconf, args.rev)
    elif direction == 'downgrade':
        alembic.command.downgrade(aconf, args.rev)
    else:
        raise RuntimeError('Unknown state')


def _action_list(args_):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(args_.others)

    base_url = CONFIG.get('url', section='app')
    url = f'{base_url}/api/hikes'
    resp = requests.get(url)
    resp.raise_for_status()

    data = resp.json()['data']
    data = map(json.dumps, data)
    data = map(print, data)
    data = list(data)


def _action_create(args_):
    ''' Create a new hike. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('--title')
    parser.add_argument('--brief')
    parser.add_argument('--description')
    parser.add_argument('--start', type=_time_type)
    parser.add_argument('--end', type=_time_type)
    parser.add_argument('--timezone', type=_tz_type, default='UTC')
    args = parser.parse_args(args_.others)

    base_url = CONFIG.get('url', section='app')
    api_key = CONFIG.get('api-key', section='app')
    url = f'{base_url}/api/hikes/new'

    data = {
        'name': args.name,
        'title': args.title,
        'brief': args.brief,
        'description': args.description,
        'start': args.start.isoformat() if args.start else args.start,
        'end': args.end.isoformat() if args.end else args.end,
        'zone': args.timezone,
    }
    headers = {
        'Api-Session': api_key,
    }

    data = data.items()
    data = filter(lambda x: x[1] is not None, data)
    data = dict(data)

    resp = requests.post(url, json=data, headers=headers, timeout=10)
    resp.raise_for_status()

    print(f' Hike: {json.dumps(resp.json(), indent=2)}')


def _action_update(args_):
    ''' Update hike info. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('hikeid', type=int)
    parser.add_argument('--name')
    parser.add_argument('--title')
    parser.add_argument('--brief')
    parser.add_argument('--description')
    parser.add_argument('--start', type=_time_type)
    parser.add_argument('--end', type=_time_type)
    parser.add_argument('--timezone', type=_tz_type)
    args = parser.parse_args(args_.others)


    base_url = CONFIG.get('url', section='app')
    api_key = CONFIG.get('api-key', section='app')
    url = f'{base_url}/api/hikes/{args.hikeid}'

    data = {
        'name': args.name,
        'title': args.title,
        'brief': args.brief,
        'description': args.description,
        'start': args.start.isoformat() if args.start else args.start,
        'end': args.end.isoformat() if args.end else args.end,
        'zone': args.timezone,
    }
    headers = {
        'Api-Session': api_key,
    }

    data = data.items()
    data = filter(lambda x: x[1] is not None, data)
    data = dict(data)

    resp = requests.post(url, json=data, headers=headers, timeout=10)
    resp.raise_for_status()

    print(' Hike: {json.dumps(resp.json(), indent=2)}')


def _action_upload(args_):
    ''' Upload pictures and GPX files to hike. '''
    parser = argparse.ArgumentParser()
    parser.add_argument('hikeid', type=int)
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args(args_.others)

    pic_files = ('.jpg', '.jpeg')
    data_files = ('.gpx',)

    for file in args.files:
        if file.suffix.lower() not in (*pic_files, *data_files):
            raise ValueError(f'Unhandlable file type {file}')

    base_url = CONFIG.get('url', section='app')
    api_key = CONFIG.get('api-key', section='app')
    headers = {'Api-Session': api_key}

    for file in args.files:
        if file.suffix.lower() in pic_files:
            url = f'{base_url}/api/pictures/hike/{args.hikeid}'
        else:
            url = f'{base_url}/api/hikes/{args.hikeid}/data'
        with open(file, 'rb') as inf:
            files = {file.name: inf}
            resp = requests.post(
                url,
                files=files,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()


def _action_process(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args(args_.others)

    base_url = CONFIG.get('url', section='app')
    api_key = CONFIG.get('api-key', section='app')
    headers = {'Api-Session': api_key}

    url = f'{base_url}/api/pictures/process?limit={args.limit}'

    resp = requests.post(
        url,
        headers=headers,
        timeout=args.timeout,
    )
    resp.raise_for_status()

    print(json.dumps(resp.json(), indent=2))


####################################################################################################

def _main():
    actions = {
        'migrate': _action_migrate,
        'list': _action_list,
        'create': _action_create,
        'update': _action_update,
        'upload': _action_upload,
        'process': _action_process,
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=list(actions.keys()),
    )
    parser.add_argument(
        'others',
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()

    actions[args.action](args)


if __name__ == '__main__':
    _main()
