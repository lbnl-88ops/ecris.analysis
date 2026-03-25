import dataclasses
import datetime as dt
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Union

import h5py
import numpy as np

from ops.ecris.operations.emittance_scan.parameters import LinearScanParameters
from ops.ecris.devices.motor_controller_specification import Axis
from ops.ecris.analysis.model.emittance_scan import EmittanceScan

DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


def _file_raw_timestamp(file: Path) -> float | None:
    try:
        return float(file.stem[-10:])
    except BaseException as e:
        logging.info(f"Failed to parse timestamp for file {file}: {e}")
        return None


def _file_formatted_timestamp(file: Path) -> str:
    raw_timestamp = _file_raw_timestamp(file)
    if raw_timestamp is not None:
        return dt.datetime.fromtimestamp(raw_timestamp).strftime(DATETIME_FORMAT)
    else:
        return "UNKNOWN"


def load_emittance_scan(filepath: Union[str, Path]) -> EmittanceScan:
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Scan file not found: {filepath}")

    with h5py.File(filepath, "r") as f:
        if "scan_data" not in f:
            raise KeyError(f"File {filepath} does not contain a 'scan_data' dataset.")
        dataset = f["scan_data"]
        data = dataset[:]
        raw_attrs = dict(dataset.attrs)

    timestamp = _file_raw_timestamp(filepath)

    param_fields = {field.name for field in dataclasses.fields(LinearScanParameters)}

    constructor_args = {}
    extra_metadata = {}

    for key, value in raw_attrs.items():
        if value == "None":
            value = None

        if key == "axis" and isinstance(value, str):
            try:
                value = Axis[value]
            except KeyError:
                pass

        if key in param_fields:
            constructor_args[key] = value
        else:
            extra_metadata[key] = value

    parameters = LinearScanParameters(**constructor_args)

    return EmittanceScan(
        data=data,
        scan_parameters=parameters,
        timestamp=timestamp,
        extra_metadata=extra_metadata if extra_metadata else None,
    )
