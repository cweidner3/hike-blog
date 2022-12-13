'''
Display Progress Info.
'''

from pathlib import Path
import sys
from typing import List


class Progress:
    ''' General progres manager. '''

    def __init__(self, total: int, no_print: bool = False) -> None:
        self._total: int = total
        self._cur: int = 0
        self._no_print: bool = no_print
        self._last_msg: str = ''

    def _print(self, perc: float):
        msg = f'{perc:.2f}%'
        if msg == self._last_msg:
            return
        print(f'\r{" " * len(self._last_msg)}', end='', file=sys.stderr)
        print(f'\r{msg}', end='', file=sys.stderr)
        self._last_msg = msg

    def handle(self, chunk_len: int) -> float:
        ''' Update the progress and print (maybe). '''
        self._cur += chunk_len
        perc = (self._cur / self._total) * 100
        if not self._no_print:
            self._print(perc)
        return perc


class FilesProgress:
    ''' Progress manager for uploading multiple files worth of data. '''

    def __init__(self, files: List[Path]) -> None:
        self._files = files
        self._file_idx: int = 0
        self._last_msg: str = ''
        self._cur: Progress = Progress(self._files[0].stat().st_size, no_print=True)

    def _print(self, perc: float):
        msg = f'({self._file_idx + 1:02d} / {len(self._files):02d}) {perc:.2f}%'
        if msg == self._last_msg:
            return
        print(f'\r{" " * len(self._last_msg)}', end='', file=sys.stderr)
        print(f'\r{msg}', end='', file=sys.stderr)
        self._last_msg = msg

    def handle(self, chunk_len: int) -> float:
        ''' Update the progress and print (maybe). '''
        perc = self._cur.handle(chunk_len)
        self._print(perc)
        return perc

    def next_file(self):
        ''' Set progress needle to the next file in the list. '''
        if self._file_idx + 1 >= len(self._files):
            return
        self._file_idx += 1
        self._cur: Progress = Progress(self._files[self._file_idx].stat().st_size, no_print=True)
