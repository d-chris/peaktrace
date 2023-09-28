import csv
import os
import time
from pathlib import Path

from .cantrace import CanTrace
from .lintrace import LinTrace


class PeakTrace:
    def __new__(cls, filename: str):
        suffix = Path(filename).suffix.casefold()

        if suffix == '.trc':
            return CanTrace(filename)

        if suffix == '.ltrc':
            return LinTrace(filename)

        raise ValueError(f'File extension {suffix} not supported')


def convert(filename: str, output: str = None, force: bool = False) -> Path:
    """converts a trace file into a csv file"""

    output = output or Path(filename).with_suffix('.csv')

    if Path(output).is_file():
        if not force:
            raise FileExistsError(f'File {output} already exists')

    trc = PeakTrace(filename)

    header = trc.keys(True)

    with open(output, 'wt', newline='') as f:
        writer = csv.DictWriter(
            f, fieldnames=header, quoting=csv.QUOTE_ALL, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(map(trc.expand, trc))

    return Path(output)


def console(filename: str, sleep: float = None, tail: bool = False) -> dict:
    if sleep is None:
        sleep = 1.0

    trc = PeakTrace(filename)

    with open(filename, mode='r') as f:
        if tail:
            f.seek(0, os.SEEK_END)

        while True:
            line = f.readline()

            if line.startswith(';'):
                continue

            itmes = line.split()

            if not itmes:
                time.sleep(sleep)
                continue

            yield trc.parse(itmes)
