import logging
import datetime as dt
from pathlib import Path

import numpy as np

from ecris.analysis.model import CSD

DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

def file_raw_timestamp(file: Path) -> float | None:
    try:
        return float(file.name[-10:])
    except BaseException as e:
        logging.info(f'Failed to parse timestamp for file {file}: {e}')
        return None

def file_formatted_timestamp(file: Path) -> str:
    raw_timestamp = file_raw_timestamp(file)
    if raw_timestamp is not None:
        return dt.datetime.fromtimestamp(raw_timestamp).strftime(DATETIME_FORMAT)
    else:
        return 'UNKNOWN'
        

def read_csd_from_file_pair(csd_file: Path) -> CSD:
    data = np.loadtxt(csd_file)
    timestamp = file_formatted_timestamp(csd_file)
    settings = {}
    with open(csd_file.with_name(csd_file.name.replace('csd', 'dsht')),'r') as f:
        for setting in f.readlines():
            _, value, name = setting.split()
            settings[name] = float(value)
    return CSD(data=data, timestamp=timestamp, settings=settings)
