"""Module for performing a polynomial fit for M/Q"""

from typing import List, Tuple, Optional

import numpy as np
from numpy.polynomial import Legendre
import scipy.optimize as opt

from ops.ecris.analysis.model import CSD, Element
from .m_over_q import estimate_m_over_q


def default_polynomial_fit(csd: CSD) -> Tuple[np.ndarray, opt.OptimizeResult]:
    return polynomial_fit_mq(
        csd,
        [Element("Oxygen", "O", 15.9949, 8)],
    )


def polynomial_fit_mq(
    csd: CSD,
    elements: List[Element],
    polynomial_order: int = 3,
    linear_bounds: Optional[Tuple[float, float]] = None,
    nonlinear_bounds: Tuple[float, float] = (-1, 1),
) -> Tuple[np.ndarray, opt.OptimizeResult]:
    if polynomial_order < 1:
        raise RuntimeError("Polynomial order must be at least linear")
    estimated_m_over_q = estimate_m_over_q(csd)

    max_x = int(np.max(estimated_m_over_q)) + 1
    x = np.linspace(0, max_x, 1000)
    _, unique_mask = np.unique(estimated_m_over_q, return_index=True)
    signal_x = estimated_m_over_q[unique_mask]
    signal = csd.beam_current[unique_mask]

    mq = np.linspace(0, max_x, 1000)
    q_values = [e.atomic_number for e in elements]
    m_values = [e.atomic_mass for e in elements]
    template = np.zeros_like(mq)
    for m, q_max in zip(m_values, q_values):
        for v in [m / q for q in range(1, q_max + 1) if m / q < max_x]:
            i = np.argmin(np.abs(mq - v))
            template[i] = 100

    def residual(P):
        polynomial = Legendre(P, window=[0, max_x], domain=[0, max_x])
        x_mapping = polynomial(signal_x)
        if not np.all(np.diff(x_mapping) > 0):
            return 0
        if not np.all(x_mapping > 0):
            return 0
        if x_mapping[-1] > 10:
            return 0
        shifted_signal = np.interp(x, x_mapping, signal)
        return -float(np.correlate(template, shifted_signal)[0])

    sb = nonlinear_bounds
    if linear_bounds is None:
        lb = (9 / max_x, 11 / max_x)
    else:
        lb = linear_bounds
    bounds = [sb, lb] + [sb] * (polynomial_order - 2)
    sol = opt.direct(residual, bounds)
    poly = Legendre(sol.x)
    return poly(estimated_m_over_q), sol
