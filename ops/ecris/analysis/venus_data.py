from pathlib import Path
from datetime import datetime, timedelta
from typing import List

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