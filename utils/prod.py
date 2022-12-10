#!/usr/bin/env python3

import re
import os
import argparse
import logging
from pathlib import Path
from alembic import migration, config
import alembic
import alembic.command

from common.config import CONFIG, get_logger, ROOT

LOG = get_logger()


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


def _main():
    actions = {
        'migrate': _action_migrate,
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
