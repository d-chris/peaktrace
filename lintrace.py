import itertools
import re


class LinTrace:
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

        return obj

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
                raise ValueError('File version not found')

    @staticmethod
    def islice(iterable, n=None):
        return itertools.islice(iterable, n)


class LinTrace10(LinTrace, version='1.0'):
    @classmethod
    def parse(cls, line: list[str]):

        reader = iter(line)

        keys = ('#', 'TIMESTAMP', 'DIRECTION', 'ID', 'LENGTH')
        values = cls.islice(reader, len(keys))

        msg = dict(zip(keys, values))

        length = int(msg['LENGTH'])
        msg['DATA'] = list(cls.islice(reader, length))

        keys = ('CHECKSUM', 'TYPE')
        values = cls.islice(reader, len(keys))
        msg.update(zip(keys, values))

        error = ' '.join(cls.islice(reader))
        if error:
            msg['ERROR'] = error

        return msg

    @classmethod
    def is_msg(cls, msg):
        return msg.get('ERROR') is None


class LinTrace11(LinTrace10, version='1.1'):
    ...
