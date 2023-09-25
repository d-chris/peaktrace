from pathlib import Path

from cantrace import CanTrace
from lintrace import LinTrace


class PeakTrace:
    def __new__(cls, filename: str):
        suffix = Path(filename).suffix.casefold()

        if suffix == '.trc':
            return CanTrace(filename)

        if suffix == '.ltrc':
            return LinTrace(filename)

        raise ValueError(f'File extension {suffix} not supported')


def main():
    def strip(msg):
        """remove (key, value) pairs from dict if value empty or '-'"""
        msg = {k: v for k, v in msg.items() if v and v != '-'}
        try:
            msg['#'] = msg['#'].rstrip(')')
        except KeyError:
            pass
        return msg

    for trace in Path('./trace').rglob('*.*trc'):
        trc = PeakTrace(trace)
        print(trc.version)

        for msg in trc:
            print(strip(msg))


if __name__ == '__main__':
    main()
