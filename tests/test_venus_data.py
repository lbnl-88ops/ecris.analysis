from pathlib import Path
from datetime import datetime

import pytest

from ops.ecris.analysis.venus_data import files_in_timeframe

def test_get_files_in_timeframe_single_day():
    files = Path('./tests/test_data').glob('*.parquet')
    FMT = '%Y-%m-%d %H:%M'
    start = datetime.strptime('2025-08-22 20:00', FMT)
    end = datetime.strptime('2025-08-22 21:00', FMT)
    found_files = files_in_timeframe(files, start, end)
    assert len(found_files) == 3

def test_get_files_in_timeframe():
    files = Path('./tests/test_data').glob('*.parquet')
    FMT = '%Y-%m-%d %H:%M'
    start = datetime.strptime('2025-08-22 20:00', FMT)
    end = datetime.strptime('2025-08-30 21:00', FMT)
    found_files = files_in_timeframe(files, start, end)
    assert len(found_files) == 11
