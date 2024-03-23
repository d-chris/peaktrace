from datetime import datetime, timedelta


def decode_starttime(timestamp: str) -> datetime:
    """
    convert starttime from trace to a datetime object
    """
    days, ms = timestamp.split(".")
    milliseconds = (24 * 60 * 60 * 1000) * float("0." + ms)

    return datetime(1899, 12, 30) + timedelta(days=int(days), milliseconds=milliseconds)


def encode_starttime(dt: datetime) -> str:
    """
    convert a datetime object to a starttime for a trace
    """
    delta = dt - datetime(1899, 12, 30)

    us = delta.seconds * 1e6 + delta.microseconds
    frac = us / (24 * 60 * 60 * 1000 * 1000)

    return str(float(delta.days) + frac)


def decode_timestamp(timestamp: str) -> datetime:
    date_format = "%d.%m.%Y %H:%M:%S.%f"

    return datetime.strptime(timestamp, date_format)


def main():
    s = decode_starttime("39878.6772258947")

    print(s)

    print(encode_starttime(s))


if __name__ == "__main__":
    main()
