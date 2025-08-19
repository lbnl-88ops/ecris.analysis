"""This module contains methods for calculating and improving
M/Q values."""
from typing import List

import numpy as np

from ops.ecris.analysis.model import CSD, Element
from ops.ecris.analysis.peaks import find_element_peaks, ElementPeaks

# measured approximate relation between the dipole hall probe 
# measure [tesla] and M/Q: alpha = B_batman[tesla]/sqrt(M/Q * Vext[kV])
_ALPHA: float = 0.00824

def scale_with_oxygen(csd: CSD) -> None:
    csd.m_over_q = estimate_m_over_q(csd)
    rescale_with_oxygen(csd)

def estimate_m_over_q(csd: CSD) -> np.ndarray:
    """Estimate a value of M/Q using the constant alpha.

    :param csd: CSD to calculate M/Q
    :type csd: CSD
    :return: array containing values of M/Q that align with the CSD arrays
    :rtype: np.ndarray
    """
    return csd.dipole_field*csd.dipole_field/_ALPHA/_ALPHA/csd.extraction_voltage

def rescale_m_over_q(m_over_q: np.ndarray, 
                     peaks: ElementPeaks) -> np.ndarray: 
    rescaled_m_over_q: np.ndarray = 1.0*m_over_q
    actual_peak_indices = peaks.indexes
    expected_peaks = peaks.m_over_q
    for i, peak_idx in enumerate(actual_peak_indices):
        if i == 0:
            rescaled_m_over_q[:peak_idx + 1] = np.linspace(m_over_q[0], 
                                                       expected_peaks[0], 
                                                       peak_idx + 1)
        else:
            rescaled_m_over_q[actual_peak_indices[i-1]:peak_idx + 1] = (
                np.linspace(expected_peaks[i-1], expected_peaks[i],
                            peak_idx - actual_peak_indices[i-1] + 1))
        rescaled_m_over_q[peak_idx:] = np.linspace(
            expected_peaks[-1], m_over_q[-1], len(m_over_q) - peak_idx)
    return rescaled_m_over_q
        
def rescale_with_oxygen(csd: CSD) -> None:
    oxygen = Element('Oxygen', 'O', 16, 8)
    rescale_with_element(csd, oxygen)

def rescale_with_element(csd: CSD, element: Element) -> None:
    if csd.m_over_q is None:
        csd.m_over_q = estimate_m_over_q(csd)
    peaks = find_element_peaks(csd, element, 0.1)
    csd.m_over_q = rescale_m_over_q(csd.m_over_q, peaks)