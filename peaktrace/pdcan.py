import os
import subprocess
from tempfile import TemporaryDirectory
from typing import List, Tuple

import pandas as pd
from pathlibutil import Path


def read_trace(filename, **kwargs) -> pd.DataFrame:
    """Reads a Peak Can .trc or .csv file and returns a pandas.DataFrame."""

    if Path(filename).suffix == ".trc":
        return CanCsv.read_trc(filename, **kwargs)

    return CanCsv.read_csv(filename, **kwargs)


def PeakFrame(filename, **kwargs) -> pd.DataFrame:
    """
    Read messages containing can-data into DataFrame from *.trc or *.csv file.
    Data bytes are integer in 'little' and 'big' endianess.
    """

    df = read_trace(filename, **kwargs).can.get_messages().reset_index(drop=True)

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

    df = df.fillna("").values.tolist()

    if columns is None:
        columns = ["Little", "Big"]

    return pd.DataFrame(map(hextoint, iter(df)), columns=columns)


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
    def type_fd(self):
        """CAN FD message types containing data."""
        return [
            "FD",
            "FB",
            "FE",
            "BI",
        ]

    @property
    def type_can(self):
        """CAN message types containing data."""
        return [
            "DT",
        ]

    @property
    def type_data(self):
        """Message types containing data."""
        return self.type_can + self.type_fd

    @property
    def type_error(self):
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
            .reset_index(drop=True)
            .astype(
                {
                    "Time": "float",
                    "Bus": "uint8",
                    "Direction": "category",
                    "Type": "category",
                    "Length": "category",
                }
            )
        )


@pd.api.extensions.register_dataframe_accessor("can")
class CanCsvAccessor(CanCsv):

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._df = pandas_obj

    @staticmethod
    def _validate(obj):
        pass

    @property
    def is_canfd(self):
        return self._df["Type"].isin(self.type_fd).any()

    def get_messages(self, msgtype: List[str] = None):
        """return entries containing a can or canfd message."""
        return self._df[self._df["Type"].isin(msgtype or self.type_data)]

    def get_id(self, id: int, extended: bool = False):
        """get all entries for a given identifier."""

        return self._df[self._df["ID"] == id]

    def get_bus(self, bus: int):
        """get all entries for a given bus."""

        return self._df[self._df["Bus"] == bus]
