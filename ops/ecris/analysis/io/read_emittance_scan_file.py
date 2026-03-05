import dataclasses
from pathlib import Path
from typing import Tuple, Dict, Any, Union

import h5py
import numpy as np

from ops.ecris.operations.emittance_scan.parameters import LinearScanParameters
from ops.ecris.devices.motor_controller_specification import Axis


def load_emittance_scan(
    filepath: Union[str, Path],
) -> Tuple[np.ndarray, LinearScanParameters, Dict[str, Any]]:
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Scan file not found: {filepath}")

    with h5py.File(filepath, "r") as f:
        if "scan_data" not in f:
            raise KeyError(f"File {filepath} does not contain a 'scan_data' dataset.")
        dataset = f["scan_data"]
        data = dataset[:]
        raw_attrs = dict(dataset.attrs)

    param_fields = {field.name for field in dataclasses.fields(LinearScanParameters)}

    constructor_args = {}
    extra_metadata = {}

    for key, value in raw_attrs.items():
        if value == "None":
            value = None

        if key == "axis" and isinstance(value, str):
            try:
                value = Axis[value]
                print(value)
            except KeyError:
                pass

        if key in param_fields:
            constructor_args[key] = value
        else:
            extra_metadata[key] = value

    parameters = LinearScanParameters(**constructor_args)

    return data, parameters, extra_metadata
