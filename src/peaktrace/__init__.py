import csv
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


def convert(filename: str, output: str = None):

    output = output or Path(filename).with_suffix('.csv')

    trc = PeakTrace(filename)

    header = []

    with open(output, 'wt', newline='') as f:
        writer = csv.DictWriter(
            f, fieldnames=header, quoting=csv.QUOTE_ALL, extrasaction='ignore')
        # writer.writeheader()
        writer.writerows(filter(trc.is_msg, trc))
