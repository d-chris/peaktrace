import functools
import os
import subprocess
from tempfile import TemporaryDirectory
from typing import List, Tuple

import numpy as np
import pandas as pd
from pathlibutil import Path


def dataframe_parquet(func=None, /, subdir=None):
    if func is None:
        return functools.partial(dataframe_parquet, subdir=subdir)

    @functools.wraps(func)
    def wrapper(file, *args, **kwargs):

        filename = Path(file)

        hash = filename.hexdigest("blake2s")

        if subdir is None:
            parquet = filename.parent / hash
        else:
            parquet = filename.parent / subdir / hash

        if parquet.is_file():
            df = pd.read_parquet(parquet)
        else:
            df = func(file, *args, **kwargs)

            parquet.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(parquet)

        return df

    return wrapper


@dataframe_parquet(subdir="__parquet__")
def read_trace(filename, **kwargs) -> pd.DataFrame:
    """Reads a PEAK Can .csv or trace file and returns a pandas.DataFrame."""

    if Path(filename).suffix.casefold() == ".csv":
        return CanCsv.read_csv(filename, **kwargs)

    return CanCsv.read_trc(filename, **kwargs)


def PeakFrame(filename, **kwargs) -> pd.DataFrame:
    """
    Read messages containing can-data into DataFrame from *.trc or *.csv file.
    Data bytes are integer in 'little' and 'big' endianess.
    """

    df = read_trace(filename, **kwargs).can.get_type()

    data = to_int(df.filter(regex=r"D\d+"))

    return df[["Time", "Bus", "ID"]].join(data)


def Id(identifier: int, extended: bool = False) -> str:
    """Format a CAN identifier as a string."""
    if isinstance(identifier, str):
        identifier = int(identifier, 16)

    if extended:
        return f"{identifier:08X}"
    return f"{identifier:04X}"


def to_int(df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
    """
    Combines all columns containing hex-strings to a single integer.

    Returns a DataFrame with the integer values in 'little' and 'big' endianess.
    """

    def hextoint(hexlist: List[str]) -> Tuple[int, int]:
        hexstr = bytes.fromhex("".join(s for s in hexlist if s))
        return (int.from_bytes(hexstr, "little"), int.from_bytes(hexstr, "big"))

    data = df.fillna("").values.tolist()

    if columns is None:
        columns = ["little", "big"]

    return pd.DataFrame(map(hextoint, data), columns=columns, index=df.index)


def diff(d: pd.Series, bits: int = 8, invalid: List[int] = None) -> pd.Series:
    """
    Calculate the difference between pulses and handle overflows for the number of bits
    and invalid values.
    """

    def uint(bits: int) -> np.dtype:
        """Return the smallest numpy data type for a given number of bits."""
        if bits <= 8:
            return np.uint8
        if bits <= 16:
            return np.uint16
        if bits <= 32:
            return np.uint32
        return np.uint64

    if invalid is None:
        invalid = []

    # remove invalid values from series
    p = d[~d.isin(invalid)]

    # calculate difference and create a new series where overflows occured
    diff = (p - p.shift(1)).dropna()
    ovfl = np.where(diff < 0, len(invalid), 0)

    # mask to stay in n-bits range
    diff %= 2**bits

    # correction for overflows
    p: pd.Series = diff - ovfl

    return p.astype(uint(bits))


def get_signal(data: int, start_bit: int, bit_length: int) -> int:
    """get a signal from a data."""
    return (data >> start_bit) & ((2**bit_length) - 1)


class CanCsv:
    @classmethod
    def header(cls, databytes: int = 64) -> List[str]:
        """Column names for a Peak Converter CSV file."""
        return [
            "Number",
            "Time",
            "Bus",
            "Direction",
            "Type",
            "ID",
            "Reserved",
            "Length",
        ] + [f"D{i}" for i in range(databytes)]

    @property
    def type_fd(self) -> List[str]:
        """CAN FD message types containing data."""
        return [
            "FD",
            "FB",
            "FE",
            "BI",
        ]

    @property
    def type_can(self) -> List[str]:
        """CAN message types containing can or lin data."""
        return [
            "DT",
        ]

    @property
    def type_data(self) -> List[str]:
        """Message types containing data."""
        return self.type_can + self.type_fd

    @property
    def type_info(self) -> List[str]:
        """Message types containing status and error information."""
        return [
            "ST",
            "ER",
            "EC",
        ]

    @staticmethod
    def convert(
        trcfile: os.PathLike, csvfile: os.PathLike, delimiter: str = ","
    ) -> Path:
        """Convert with Peak Converter a *.trc to a *.csv."""

        trc = Path(trcfile).resolve(True)
        csv = Path(csvfile)

        with Path(__file__).parent:
            subprocess.run(
                [
                    "./bin/PEAK-Converter.exe",
                    str(trc),
                    "/TF=CSV",
                    f"/TD={csv.parent}",
                    f"/TN={csv.name}",
                    f"/CS={delimiter}",
                    "/OE",
                ],
                capture_output=True,
            ).check_returncode()

        return csv

    @classmethod
    def read_trc(
        cls,
        filename: os.PathLike,
        delimiter: str = ",",
        outpath: os.PathLike = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Read a Peak Trace *.trc into a DataFrame."""

        with TemporaryDirectory() as tmpdir:
            if outpath is None:
                csvname = Path(tmpdir).joinpath("temp.csv")
            else:
                csvname = Path(outpath) / Path(filename).with_suffix(".csv").name

            csvfile = cls.convert(filename, csvname, delimiter=delimiter)

            return cls.read_csv(csvfile, delimiter=delimiter, **kwargs)

    @classmethod
    def read_csv(
        cls,
        filename: os.PathLike,
        delimiter: str = ",",
        on_bad_lines="warn",
    ):
        """Read a Peak Converter *.csv into a DataFrame."""
        return (
            pd.read_csv(
                filename,
                skiprows=25,
                delimiter=delimiter,
                header=None,
                names=cls.header(),
                index_col=0,
                na_values=["", "-", "--", "None"],
                keep_default_na=False,
                on_bad_lines=on_bad_lines,
                dtype=str,
            )
            .dropna(axis=1, how="all")
            .astype(
                {
                    "Time": "float",
                    "Bus": "uint8",
                    "Direction": "category",
                    "Type": "category",
                    "Length": "uint8",
                }
            )
        )


@pd.api.extensions.register_series_accessor("can")
class CanSeriesAccessor:
    def __init__(self, pandas_obj: pd.Series) -> None:
        self._s = pandas_obj

    def diff(self, bits: int = 8, invalid: List[int] = None) -> pd.Series:
        """Calculate the difference between pulses and handle overflows."""
        return diff(self._s, bits=bits, invalid=invalid)

    def signal(self, start_bit: int, bit_length: int) -> pd.Series:
        """get a signal from a data."""
        return self._s.apply(get_signal, start_bit=start_bit, bit_length=bit_length)


@pd.api.extensions.register_dataframe_accessor("can")
class CanCsvAccessor(CanCsv):

    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        self._df = pandas_obj

    @property
    def is_canfd(self) -> bool:
        """True when the DataFrame contains CAN FD messages."""

        return self._df["Type"].isin(self.type_fd).any()

    def get_type(self, type: List[str] = None) -> pd.DataFrame:
        """return entries containing a can or canfd message."""

        return self._df[self._df["Type"].isin(type or self.type_data)]

    def get_id(self, id: int, extended: bool = False, bus: int = None) -> pd.DataFrame:
        """get all entries for a given identifier from a bus."""

        expr = f"ID == '{Id(id, extended)}'"

        if bus is not None:
            expr = f"Bus == {int(bus)} and {expr}"

        return self._df.query(expr)

    def get_bus(self, bus: int) -> pd.DataFrame:
        """get all entries for a given bus."""

        return self._df[self._df["Bus"] == bus]

    def get_signal(
        self,
        start_bit: int,
        bit_length: int,
        byteorder: str = "little",
        inplace: bool = False,
    ) -> pd.Series:

        data = self._df[byteorder].values.tolist()
        func = functools.partial(get_signal, start_bit=start_bit, bit_length=bit_length)
        name = f"{byteorder}({start_bit},{bit_length})"

        d = pd.Series(
            map(func, data),
            index=self._df.index,
            name=name,
        )

        if inplace is False:
            return d

        if isinstance(inplace, str):
            self._df[inplace] = d
        else:
            self._df[d.name] = d

        return d

    def diff(self, column: str, bits: int = 8, invalid: List[int] = None) -> pd.Series:
        """Calculate the difference between pulses and handle overflows."""
        return diff(self._df[column], bits=bits, invalid=invalid)
