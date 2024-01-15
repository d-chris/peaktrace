import itertools
import re


class CanTrace:
    _parser = {}

    def __init_subclass__(cls, version, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._parser[version] = cls

    def __new__(cls, filename: str):
        version = cls.fileversion(filename)

        try:
            subclass = cls._parser[version]
        except KeyError:
            raise ValueError(f'Version {version} not supported')

        obj = object.__new__(subclass)

        obj._filename = filename
        obj._version = version
        obj._format = 'can'

        return obj

    @property
    def format(self):
        return self._format

    @property
    def version(self):
        """file version of the trace"""
        return self._version

    @classmethod
    def parse(cls, line: list[str]):
        """returns a dictionary with the parsed message"""
        raise NotImplementedError

    @classmethod
    def is_msg(cls, msg):
        """returns False if msg is an error message or a remote request"""
        raise NotImplementedError

    def expand(self, msg):
        """expand all dictionary values that are lists into multiple keys"""
        m = msg.copy()

        for key, value in msg.items():
            if not isinstance(value, list):
                continue

            for i, item in enumerate(m.pop(key)):
                m[f'{key}{i:02d}'] = item

        return m

    def __iter__(self):
        with open(self._filename, 'r') as f:
            for line in f:
                if line.startswith(';'):
                    continue

                items = line.split()

                if not items:
                    continue

                yield self.parse(items)

    @staticmethod
    def fileversion(file: str):
        with open(file, 'r') as f:
            s = f.readline()

            match = re.search(r'(?<=^;\$FILEVERSION=)\S+', s)

            try:
                return match.group(0)
            except AttributeError:
                if not s.startswith(';###'):
                    raise ValueError('File version not found')

                return '1.0'

    @staticmethod
    def islice(iterable, n: int = None):
        return itertools.islice(iterable, n)

    @classmethod
    def _key_data(cls, expand: bool = False) -> tuple[str]:
        """return the column header for data"""
        if expand:
            return tuple(f'DATA{i:02d}' for i in range(cls.DATA_MAX))

        return ('DATA',)

    @classmethod
    def _key_error(cls, expand: bool = False) -> tuple[str]:
        """return the column header for error"""
        if expand:
            return tuple(f'ERROR{i:02d}' for i in range(cls.ERROR_MAX))

        return ('ERROR',)

    @classmethod
    def keys(cls, expand: bool = False) -> tuple[str]:
        """return the keys of the message dictionary"""
        raise NotImplementedError


class CanTrace10(CanTrace, version='1.0'):
    DATA_MAX = 8
    ERROR_MAX = 4

    @classmethod
    def keys(cls, expand=False):
        return (
            '#',
            'TIMESTAMP',
            'ID',
            'LENGTH',
        ) + cls._key_data(expand) + cls._key_error(expand) + ('EVENT',)

    @classmethod
    def parse(cls, line: list[str]):
        reader = iter(line)

        keys = ('#', 'TIMESTAMP', 'ID', 'LENGTH')
        values = cls.islice(reader, len(keys))

        msg = dict(zip(keys, values))

        if msg['ID'] == 'FFFFFFFF':
            msg['ERROR'] = [
                x for x in cls.islice(reader, 8)
                if not x == '--'
            ]
            msg['EVENT'] = ' '.join(cls.islice(reader))
        else:
            data0 = next(reader)

            if data0 == 'ERROR':
                msg['ERROR'] = list(cls.islice(reader))
            else:
                msg['DATA'] = [data0] + list(cls.islice(reader))

        return msg

    @classmethod
    def is_msg(cls, msg):
        if msg.get('ERROR'):
            return False

        data = msg.get('DATA', ['CD'])
        if data[0] == 'RTR':
            return False

        return True


class CanTrace11(CanTrace10, version='1.1'):
    @classmethod
    def keys(cls, expand=False):
        return (
            '#',
            'TIMESTAMP',
            'TYPE',
            'ID',
            'LENGTH',
        ) + cls._key_data(expand) + cls._key_error(expand) + ('EVENT',)

    @classmethod
    def parse(cls, line: list[str]):

        reader = iter(line)

        keys = ('#', 'TIMESTAMP', 'TYPE', 'ID', 'LENGTH')
        values = cls.islice(reader, len(keys))

        msg = dict(zip(keys, values))

        if msg['TYPE'] in ('Rx', 'Tx'):
            msg['DATA'] = list(cls.islice(reader))
        else:
            msg['ERROR'] = list(cls.islice(reader, 4))
            msg['EVENT'] = ' '.join(cls.islice(reader))

        return msg


class CanTrace12(CanTrace11, version='1.2'):
    @classmethod
    def keys(cls, expand=False):
        return (
            '#',
            'TIMESTAMP',
            'BUS',
            'TYPE',
            'ID',
            'LENGTH',
        ) + cls._key_data(expand) + cls._key_error(expand) + ('EVENT',)

    @classmethod
    def parse(cls, line: list[str]):

        reader = iter(line)

        keys = ('#', 'TIMESTAMP', 'BUS', 'TYPE', 'ID', 'LENGTH')
        values = cls.islice(reader, len(keys))

        msg = dict(zip(keys, values))

        if msg['TYPE'] in ('Rx', 'Tx'):
            msg['DATA'] = list(cls.islice(reader))
        else:
            msg['ERROR'] = list(cls.islice(reader, 4))
            msg['EVENT'] = ' '.join(cls.islice(reader))

        return msg


class CanTrace13(CanTrace12, version='1.3'):
    @classmethod
    def parse(cls, line: list[str]):

        reader = iter(line)

        keys = ('#', 'TIMESTAMP', 'BUS', 'TYPE', 'ID', 'REVERSED', 'LENGTH')
        values = cls.islice(reader, len(keys))

        msg = dict(zip(keys, values))

        if msg['TYPE'] in ('Rx', 'Tx'):
            msg['DATA'] = list(cls.islice(reader))
        else:
            msg['ERROR'] = list(itertools.islice(reader, 4))
            msg['EVENT'] = ' '.join(cls.islice(reader))

        return msg


class CanTrace20(CanTrace, version='2.0'):
    DATA_MAX = 64
    ERROR_MAX = 5

    @classmethod
    def keys(cls, expand=False):
        return (
            '#',
            'TIMESTAMP',
            'TYPE',
            'ID',
            'DIRECTION',
            'LENGTH',
        ) + cls._key_data(expand) + cls._key_error(expand)

    @classmethod
    def parse(cls, line: list[str]):

        reader = iter(line)

        keys = ('#', 'TIMESTAMP', 'TYPE')
        values = cls.islice(reader, len(keys))

        msg = dict(zip(keys, values))

        if msg['TYPE'] in ('ST', 'ER', 'EC'):
            msg['DIRECTION'] = next(reader)
            msg['ERROR'] = list(cls.islice(reader))
        else:
            keys = ('ID', 'DIRECTION', 'LENGTH')
            values = cls.islice(reader, len(keys))

            msg.update(zip(keys, values))
            msg['DATA'] = list(cls.islice(reader))

        return msg

    @classmethod
    def is_msg(cls, msg):
        return msg['TYPE'] not in ('ST', 'ER', 'EC', 'RR')


class CanTrace21(CanTrace20, version='2.1'):
    @classmethod
    def keys(cls, expand=False):
        return (
            '#',
            'TIMESTAMP',
            'TYPE',
            'BUS',
            'ID',
            'DIRECTION',
            'LENGTH',
        ) + cls._key_data(expand) + cls._key_error(expand) + ('EVENT',)

    @classmethod
    def parse(cls, line: list[str]):

        reader = iter(line)

        keys = ('#', 'TIMESTAMP', 'TYPE', 'BUS')
        values = cls.islice(reader, len(keys))

        msg = dict(zip(keys, values))

        if msg['TYPE'] == 'EV':
            msg['EVENT'] = ' '.join(cls.islice(reader))
        else:
            key = ('ID', 'DIRECTION', 'RESERVED', 'LENGTH')
            values = cls.islice(reader, len(key))

            msg.update(zip(key, values))

            if msg['TYPE'] in ('ST', 'ER', 'EC'):
                key = 'ERROR'
            else:
                key = 'DATA'

            msg[key] = list(cls.islice(reader))

        return msg

    @classmethod
    def is_msg(cls, msg):
        if msg['TYPE'] == 'EV':
            return False

        return super().is_msg(msg)
