'''
Merges compose yaml files such that the proceeding overwrites the previous in order to implement
iterative compose specs.
'''

import argparse
from pathlib import Path
import io
from typing import Any, Union

import yaml


def _merge_docs(docold: dict, docnew: dict) -> dict:
    def _merge(oldval: Any, newval: Any) -> Any:
        if isinstance(oldval, dict) and isinstance(newval, dict):
            for key, value in newval.items():
                if value is None:
                    oldval.pop(key)
                else:
                    oldval.update({key: _merge(oldval.get(key), value)})
            return oldval
        return newval

    assert isinstance(docold, dict) and isinstance(docnew, dict)

    for key, value in docnew.items():
        if value is None:
            docold.pop(key)
        else:
            docold.update({key: _merge(docold.get(key), value)})
    return docold


def _outdoc(value: str) -> Union[str, Path]:
    if value == '-':
        return '-'
    return Path(value)


def _main():
    parser = argparse.ArgumentParser(
        description=__doc__,
    )
    parser.add_argument(
        'outfile',
        type=_outdoc,
        help='Output docker-compose file to make.',
    )
    parser.add_argument(
        'infiles',
        type=Path,
        nargs='+',
        help='Source files to merge.',
    )
    args = parser.parse_args()

    document = {}
    for file in args.infiles:
        newdoc = yaml.safe_load(io.StringIO(file.read_text(encoding='utf-8')))
        document = _merge_docs(document, newdoc)

    if isinstance(args.outfile, Path):
        args.outfile.write_text(yaml.dump(document), encoding='utf-8')
    else:
        print(yaml.dump(document))


if __name__ == '__main__':
    _main()
