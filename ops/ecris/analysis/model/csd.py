from typing import Dict, Optional

import numpy as np

class CSD:
    def __init__(self, data: np.ndarray, 
                 timestamp: str,
                 settings: Optional[Dict[str, float]] = None) -> None:
        self.data = data
        self.settings = settings
        self.timestamp = timestamp
        self._m_over_q: np.ndarray | None = None
        if self.settings is not None:
            try:
                self.settings['ht_oven_w'] = (
                    self.settings['ht_oven_i']
                    * self.settings['ht_oven_v']
                )
            except KeyError:
                self.settings['ht_oven_w'] = -1

    @property
    def m_over_q(self) -> np.ndarray | None:
        return self._m_over_q

    @m_over_q.setter
    def m_over_q(self, to_set: np.ndarray) -> np.ndarray:
        self._m_over_q = to_set
        return self._m_over_q

    @property
    def time(self) -> np.ndarray:
        return self.data[:,0]

    @property
    def dipole_current(self) -> np.ndarray:
        """Dipole current in micro-amps (A)"""
        return self.data[:,1]*1E6

    @property
    def dipole_field(self) -> np.ndarray:
        """Dipole field in Tesla (T)"""
        return self.data[:,2]

    @property
    def beam_current(self) -> np.ndarray:
        """Beam current in micro amps (A)"""
        return self.data[:,3]*1E6

    @property
    def extraction_voltage(self) -> float:
        """Extraction voltage in kilovolts (kV)"""
        return self.settings['extraction_v']
