import json
import re
from tempfile import NamedTemporaryFile

import pendulum
import requests
from pathlibutil import Path


class Pendulum:
    """
    Wrapper class to parse a timestamp, and returns a pendulum instance

    >>> Pendulum('Mon, 06 May 2024 09:17:57 GMT')
    DateTime(2024, 5, 6, 9, 17, 57, tzinfo=Timezone('GMT'))

    >>> Pendulum('2024-05-06 09:17:57+00:00')
    DateTime(2024, 5, 6, 9, 17, 57, tzinfo=FixedTimezone(0, name="+00:00"))

    >>> Pendulum('Mon, 06 May 2024 09:17:57 GMT') == Pendulum('2024-05-06 09:17:57+00:00')
    True
    """

    format = "ddd, DD MMM YYYY HH:mm:ss"
    regex = re.compile(r"(?P<time>.*?) ?(?P<tz>[A-Z]{3})?$")

    def __new__(self, timestamp: str) -> pendulum.DateTime:
        """
        Parse a timestamp and return a pendulum instance
        """

        try:
            return pendulum.parse(timestamp)
        except pendulum.parsing.exceptions.ParserError:
            return self.parse(timestamp)

    @classmethod
    def parse(cls, timestamp: str) -> pendulum.DateTime:
        """
        Costum parser to for format, 'Mon, 06 May 2024 09:17:57 GMT'
        """
        match = cls.regex.search(timestamp)

        return pendulum.from_format(
            match.group("time"),
            cls.format,
            tz=match.group("tz"),
        )


def modified(
    url: str = "https://www.peak-system.com/fileadmin/media/files/PEAK-Converter.zip",
    time: pendulum.DateTime = None,
) -> pendulum.DateTime | None:
    """
    Return None if the url header indicates that the target was not modified after the
    given time.
    """

    response = requests.head(url)

    if not response.ok:
        return None

    try:
        timestamp = Pendulum(response.headers["Last-Modified"])

    except (KeyError, pendulum.parsing.exceptions.ParserError):
        return None

    if time is None or timestamp > time:
        return timestamp

    return None


def download(
    url: str = "https://www.peak-system.com/fileadmin/media/files/PEAK-Converter.zip",
) -> Path | None:
    """
    Download a zip file from the given url into a temporary directory
    """

    chunk = 8192

    with NamedTemporaryFile(delete=False, buffering=chunk, suffix=".zip") as file:
        response = requests.get(url, stream=True)

        if (
            not response.ok
            or response.headers.get("Content-Type", "") != "application/zip"
        ):
            return None

        for chunk in response.iter_content(chunk_size=chunk):
            file.write(chunk)

    return Path(file.name)


def unpack(file: Path, destination: str = None) -> Path:
    """
    Unpack a given archive into the destination directory and delete the original file
    """
    try:
        return file.unpack_archive(destination or Path(__file__).parent)
    except Exception:
        return None
    finally:
        file.unlink(missing_ok=True)


def load(file: str) -> dict:
    try:
        file = Path(file).resolve(True)
    except FileNotFoundError:
        return {}

    return json.loads(file.read_text())


def write(data: dict, file: str) -> None:
    file = Path(file)
    file.write_text(json.dumps(data, indent=4))


if __name__ == "__main__":
    url = "https://www.peak-system.com/fileadmin/media/files/PEAK-Converter.zip"
    file = Path(__file__).parent / Path(url).with_suffix(".json").name

    data = load(file)
    data["url"] = url

    try:
        mtime = Pendulum(data["last-modified"])
    except KeyError:
        mtime = None

    time = modified(url, time=mtime)

    if time is None:
        raise SystemExit(1)

    data["last-modified"] = str(time)

    zip = download(url)

    if not zip:
        raise SystemExit(2)

    data["sha256"] = zip.hexdigest("sha256")

    unpack(zip)

    write(data, file)

    raise SystemExit(0)
