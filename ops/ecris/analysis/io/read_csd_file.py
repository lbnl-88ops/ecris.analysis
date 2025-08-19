import logging
import datetime as dt
from pathlib import Path

import numpy as np

from ops.ecris.analysis.model import CSD

DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

def _file_raw_timestamp(file: Path) -> float | None:
    try:
        return float(file.name[-10:])
    except BaseException as e:
        logging.info(f'Failed to parse timestamp for file {file}: {e}')
        return None

def _file_formatted_timestamp(file: Path) -> str:
    raw_timestamp = _file_raw_timestamp(file)
    if raw_timestamp is not None:
        return dt.datetime.fromtimestamp(raw_timestamp).strftime(DATETIME_FORMAT)
    else:
        return 'UNKNOWN'
        

def read_csd_from_file_pair(csd_file: Path) -> CSD:
    data = np.loadtxt(csd_file)
    timestamp = _file_formatted_timestamp(csd_file)
    settings = {}
    datasheet = csd_file.with_name(csd_file.name.replace('csd', 'dsht')) 
    if not datasheet.exists():
        logging.error('No datasheet file found, loading raw data only')

    else:
        try:
            with open(datasheet, 'r') as f:
                for setting in f.readlines():
                    _, value, name = setting.split()
                    settings[name] = float(value)
        except BaseException as e:
            logging.error(f'Error reading datasheet file: {e}')
    return CSD(data=data, timestamp=timestamp, settings=settings)
