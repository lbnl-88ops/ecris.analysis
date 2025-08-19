from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from ecris.analysis.model import CSD, Element

@dataclass
class Peak:
    m_over_q: float
    beam_current: float
    index: int
    use_peak: bool = True

class ElementPeaks:
    def __init__(self, peaks: List[Peak]) -> None:
        self.peaks = sorted(peaks, key=lambda p: p.m_over_q)

    @property
    def m_over_q(self) -> np.ndarray:
        return np.array([p.m_over_q for p in self.peaks if p.use_peak])

    @property
    def beam_current(self) -> np.ndarray:
        return np.array([p.beam_current for p in self.peaks if p.use_peak])
    
    @property
    def indexes(self) -> List[int]:
        return [p.index for p in self.peaks if p.use_peak]

def find_element_peaks(csd: CSD, element: Element, peak_width: float = 0.1) -> ElementPeaks:
    if csd.m_over_q is None:
        raise RuntimeError('CSD m_over_q not set, cannot seek peaks')
    found: List[Peak] = []
    peak_m_over_q: List[float] = [float(element.atomic_mass)/float(q) 
                                  for q in range(1, element.atomic_number + 1)]
    peak_m_over_q.sort()
    peak_m_over_q = [mq for mq in peak_m_over_q if mq < csd.m_over_q.max()]
    found_peaks: List[int] = []
    for expected_peak in peak_m_over_q:
        istart = np.argmax(csd.m_over_q>expected_peak-peak_width)
        iend = np.argmin(csd.m_over_q<expected_peak+peak_width)
        idx = int(istart + np.argmax(csd.beam_current[istart:iend+1]))
        current = csd.beam_current[idx]
        found.append(Peak(expected_peak, current, idx))
    return ElementPeaks(found)

def calculate_element_yield(csd: CSD, element: Element, peaks: ElementPeaks) -> Tuple[np.ndarray, np.ndarray]:
    q_values = np.divide(element.atomic_mass, peaks.m_over_q)
    return q_values, np.divide(peaks.beam_current, q_values)
    