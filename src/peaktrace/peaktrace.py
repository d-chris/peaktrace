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
