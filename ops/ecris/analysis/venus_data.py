import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

_FILE_DATE_FORMAT = '%Y_%m_%d_%H_%M_%S'

def get_file_timestamp(file: Path) -> datetime:
    return datetime.strptime(file.stem[11:], _FILE_DATE_FORMAT)

def files_in_timeframe(files, start: datetime, stop: datetime) -> List[Path]:
    files_with_dates = {get_file_timestamp(f): f for f in list(files)}

    files_to_load = []
    for date, file in sorted(files_with_dates.items()):
        if start <= date <= stop:
            files_to_load.append(file)
        elif start <= date + timedelta(days=1) <= stop:
            files_to_load.append(file)
        elif start <= date - timedelta(days=1) <= stop:
            files_to_load.append(file)
        elif date > stop:
            break 
    return files_to_load

def get_all_venus_data(path: Path, start: datetime, stop: datetime) -> pd.DataFrame:
    files_to_load = files_in_timeframe(path.glob('*.parquet'), start, stop)
    if not files_to_load:
        raise ValueError('No parquet files found for provided time span')
    return pd.concat([pd.read_parquet(f) for f in files_to_load])

def get_venus_data(path: Path, data_label: str | List[str], start: datetime, stop: datetime) -> pd.DataFrame:
    if isinstance(data_label, str):
        data_labels = ['time', data_label]
    else:
        data_labels = ['time'] + data_label

    all_data = get_all_venus_data(path, start, stop)
    all_data['time'] = all_data['time'].apply(datetime.fromtimestamp)
    return all_data[(start <= all_data['time']) & (all_data['time'] <= stop)].loc[:, data_labels]
