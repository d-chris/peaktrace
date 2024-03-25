import pandas as pd
import pytest

from peaktrace import read_trace
from peaktrace.pdcan import Id, PeakFrame


@pytest.mark.parametrize(
    "file",
    [
        "examples/csv/2-1.trc.csv",
        "examples/trc/2-1.trc",
    ],
)
def test_reader(file):
    df = read_trace(file)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (13, 18)


@pytest.mark.parametrize(
    "id, ext, result",
    [
        (291, False, "0123"),
        (291, True, "00000123"),
        (0x123, False, "0123"),
        (0x123, True, "00000123"),
        ("123", False, "0123"),
        ("123", True, "00000123"),
        ("0x123", False, "0123"),
        ("0x123", True, "00000123"),
        ("00000123", False, "0123"),
        ("0123", True, "00000123"),
    ],
)
def test_id(id, ext, result):
    identifier = Id(id, ext)
    assert isinstance(identifier, str)
    assert identifier == result


@pytest.mark.parametrize(
    "id, result",
    [
        ("00000123", "0123"),
        ("123", "0123"),
    ],
)
def test_id_default(id, result):
    identifier = Id(id)
    assert isinstance(identifier, str)
    assert identifier == result


def test_peakframe():
    df = PeakFrame("./examples/csv/2-1.trc.csv")

    assert isinstance(df, pd.DataFrame)
