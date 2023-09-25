from pathlib import Path

from cantrace import CanTrace


class PeakTrace:
    def __new__(cls, filename: str):
        suffix = Path(filename).suffix

        if suffix.casefold() == '.trc':
            return CanTrace(filename)

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

    for trace in Path('./trc').glob('*.trc'):
        trc = PeakTrace(trace)
        print(trc.version)

        for msg in filter(trc.is_msg, trc):
            print(strip(msg))


if __name__ == '__main__':
    main()
