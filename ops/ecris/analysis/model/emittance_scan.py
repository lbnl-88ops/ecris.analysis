from typing import Dict, Any, Optional

import numpy as np

from ops.ecris.operations.emittance_scan.parameters import LinearScanParameters


class EmittanceScan:
    def __init__(
        self,
        timestamp: str,
        data: np.ndarray,
        scan_parameters: LinearScanParameters,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ):
        self._data: np.ndarray = data
        self.timestamp = timestamp
        self._scan_parameters: LinearScanParameters = scan_parameters
        self.extra_metadata: Dict[str, Any] | None = extra_metadata

    @property
    def data(self) -> np.ndarray:
        return self._data

    @property
    def scan_parameters(self) -> LinearScanParameters:
        return self._scan_parameters

    @property
    def position_range(self) -> np.ndarray:
        return np.arange(
            self.scan_parameters.position_min,
            self.scan_parameters.position_max + self.scan_parameters.position_step,
            self.scan_parameters.position_step,
        )

    @property
    def divergence_range(self) -> np.ndarray:
        return np.arange(
            self.scan_parameters.divergence_min,
            self.scan_parameters.divergence_max + self.scan_parameters.divergence_step,
            self.scan_parameters.divergence_step,
        )
