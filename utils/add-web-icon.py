#!/usr/bin/env python3
'''
Utility to convert the font awesome svgs to pngs for use in the maps. Just provide the font awesome
import name (i.e. what is used to import icons) or multiple names and they will be created in the
`web/src/icons/` folder.
'''

import argparse
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

LOG = logging.getLogger('script')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(int(os.environ['LOG_LEVEL']) if 'LOG_LEVEL' in os.environ else logging.INFO)

HERE = Path(__file__).parent.resolve()
SRC_PATH = Path(HERE, '../web/node_modules/@fortawesome/free-solid-svg-icons').resolve()
DEST_PATH = Path(HERE, '../web/src/icons').resolve()

DATA_PAT = re.compile(r'svgPathData\s*\=\s*[\'"](.*)[\'"];?$', flags=re.MULTILINE)
HEIGHT_PAT = re.compile(r'height\s*=\s*(\d+)', flags=re.MULTILINE)
WIDTH_PAT = re.compile(r'width\s*=\s*(\d+)', flags=re.MULTILINE)


def _convert_to_png(icon_xml: str, dest_path: Path) -> Path:
    LOG.debug('SVG XML Data: %s', icon_xml.encode())
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir).resolve()
        svg_file = Path(tmppath, '1.svg')
        svg_file.write_text(icon_xml, encoding='utf-8')
        tmp_dest = Path(tmppath, '1.png')
        subprocess.run(
            [
                'convert',
                '-verbose',
                '-background', 'none',
                f'{svg_file}',
                f'{tmp_dest}',
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        shutil.move(tmp_dest, dest_path)
    return dest_path


def _create_svg_xml(data: str) -> str:
    LOG.debug('JS data to parse info from: %s', data.encode())
    path_data = DATA_PAT.search(data)
    height = HEIGHT_PAT.search(data)
    width = WIDTH_PAT.search(data)
    assert path_data is not None, 'Failed to parse JS file for path data'
    assert height is not None, 'Failed to parse JS file for height'
    assert width is not None, 'Failed to parse JS file for width'
    path_data = path_data.group(1)
    height = height.group(1)
    width = width.group(1)
    doc = f'''\
            <svg xmlns="http://www.w3.org/2000/svg" viewPort="0 0 {width} {height}">
            <path d="{path_data}" />
        </svg>
    '''
    return doc


def _handle_icon(icon: str) -> Path:
    LOG.info('Importing icon %s', icon)
    src_path = Path(SRC_PATH, f'{icon}.js')
    assert src_path.exists(), f'Unable to find "{src_path}"'
    LOG.info('Using source file %s', src_path)
    dest_path = Path(DEST_PATH, f'{icon}.png')
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    LOG.info('Destination file %s', dest_path)
    xml = _create_svg_xml(src_path.read_text(encoding='utf-8'))
    return _convert_to_png(xml, dest_path)


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'icon',
        nargs='+',
        help='The name used when importing with nodejs',
    )
    args = parser.parse_args()

    list(map(_handle_icon, args.icon))


_main()
