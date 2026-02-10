"""Module for performing a polynomial fit for M/Q"""

from typing import List, Tuple, Optional

import numpy as np
from numpy.polynomial import Legendre
import scipy.optimize as opt
from scipy.signal import find_peaks

from ops.ecris.analysis.model import CSD, Element
from ops.ecris.analysis.csd.m_over_q import estimate_m_over_q


def default_polynomial_fit(csd: CSD) -> Tuple[np.ndarray, opt.OptimizeResult]:
    return polynomial_fit_mq(
        csd,
        [Element("Oxygen", "O", 15.9949, 8)],
    )


def polynomial_fit_mq(
    csd: CSD,
    elements: List[Element],
    polynomial_order: int = 3,
    linear_bounds: Optional[Tuple[float, float]] = (0.95, 1.05),
    nonlinear_bounds: Tuple[float, float] = (-1e-3, 1e-3),
    max_iterations: int = 1000,
    max_function_evaluations: Optional[int] = None,
    optimize_on_failure: bool = False,
    always_optimize: bool = False,
) -> Tuple[np.ndarray, opt.OptimizeResult]:
    if polynomial_order < 1:
        raise RuntimeError("Polynomial order must be at least linear")
    estimated_m_over_q = estimate_m_over_q(csd)
    peaks, _ = find_peaks(csd.beam_current)
    potential_h_lines = [estimated_m_over_q[int(p)] for p in peaks]
    h_loc = estimated_m_over_q[np.argmin(np.abs([v - 1 for v in potential_h_lines]))]
    estimated_m_over_q = estimated_m_over_q - h_loc

    max_x = int(np.max(estimated_m_over_q))
    _, unique_mask = np.unique(estimated_m_over_q, return_index=True)
    signal_x = estimated_m_over_q[unique_mask]
    signal = csd.beam_current[unique_mask]

    q_values = [e.atomic_number for e in elements]
    m_values = [e.atomic_mass for e in elements]

    def residual(P):
        polynomial = Legendre([0, *P], window=[0, max_x], domain=[0, max_x])
        template = np.zeros_like(signal_x)
        penalty = 0
        for m, q_max in zip(m_values, q_values):
            for v in [m / q - h_loc for q in range(1, q_max + 1) if m / q < max_x]:
                v_x = polynomial(v)
                if v_x > max_x:
                    penalty += v_x - max_x
                elif v_x < 0:
                    penalty += np.abs(v_x)
                i = np.argmin(np.abs(signal_x - polynomial(v)))
                template[i] = 100
        return -float(np.correlate(template, signal)[0]) + 1e4 * penalty**2

    sb = nonlinear_bounds
    lb = linear_bounds
    bounds = [lb] + [sb] * (polynomial_order - 2)
    sol = opt.direct(
        residual,
        bounds,
        maxfun=max_function_evaluations,
        maxiter=max_iterations,
        locally_biased=False,
        vol_tol=1e-16 / (10 * (polynomial_order - 2)),
    )
    if always_optimize or (optimize_on_failure and not sol.success):
        sol = opt.minimize(residual, sol.x, bounds=bounds, method="Nelder-Mead")
    poly = Legendre([0, *sol.x])
    fine_mq = np.linspace(0, max_x, 10000)
    fit_x_mapping = poly(fine_mq)
    x_to_mq_interp = np.interp(estimated_m_over_q, fit_x_mapping, fine_mq)
    return x_to_mq_interp + h_loc, sol
