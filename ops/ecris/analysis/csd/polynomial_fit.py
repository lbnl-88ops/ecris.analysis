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

def _make_polynomial(P, max_x: float):
    linear_scale, *c = P
    # create legendre without linear 
    poly = Legendre([0.0, 0.0, *c], domain=[0, max_x])
    return lambda v: linear_scale*v + poly(v) - (poly(0.0))

def prepare_scoring(csd, signal_x, signal, elements, max_x,
                    resolving_power, q_cap=None):
    lo = signal[signal < np.percentile(signal, 40)]
    sigma = 1.4826 * np.median(np.abs(lo - np.median(lo)))

    sy = np.log1p(np.clip(signal, 0.0, None) / (3.0 * sigma))
    sy /= max(sy.max(), 1e-12)

    pos = []
    for e in elements:
        qmax = e.atomic_number if q_cap is None else min(e.atomic_number, q_cap)
        for q in range(1, qmax + 1):
            v = e.atomic_mass / q - 1.0          # H-shifted frame
            if 0.0 <= v <= max_x:
                pos.append(v)
    lines = np.unique(np.round(pos, 6))          # collapse degenerate positions

    return signal_x, sy, lines, sigma


def matched_score(sx, sy, centers, width, nsig=4.0):
    """Mean local intensity under a Gaussian kernel at each predicted line."""
    w = np.maximum(width, 1e-6)
    a = np.searchsorted(sx, centers - nsig * w)
    b = np.searchsorted(sx, centers + nsig * w)
    total = 0.0
    for c, wi, i0, i1 in zip(centers, w, a, b):
        if i1 <= i0:
            continue
        k = np.exp(-0.5 * ((sx[i0:i1] - c) / wi) ** 2)
        ks = k.sum()
        if ks > 0:
            total += float(sy[i0:i1] @ k) / ks
    return total

def make_residual(sx, sy, lines, widths, max_x, n_check=512):
    n_lines = len(lines)
    vgrid = np.linspace(0.0, max_x, n_check)

    def residual(P):
        f = _make_polynomial(P, max_x)
        g = f(vgrid)
        if np.any(np.diff(g) <= 0):              # reject non-monotonic maps
            return 1e6

        v_x = f(lines)
        out_lo = np.clip(-v_x, 0, None).sum()
        out_hi = np.clip(v_x - max_x, 0, None).sum()
        penalty = out_lo + out_hi

        inb = (v_x >= 0) & (v_x <= max_x)
        s = matched_score(sx, sy, v_x[inb], widths[inb])

        return -s / n_lines + 10.0 * penalty ** 2

    return residual

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
    j = int(np.argmin(np.abs(np.array(potential_h_lines) - 1.0)))
    h_loc = potential_h_lines[j]
    estimated_m_over_q = estimated_m_over_q - h_loc

    max_x = float(np.max(estimated_m_over_q))
    _, unique_mask = np.unique(estimated_m_over_q, return_index=True)
    signal_x = estimated_m_over_q[unique_mask]
    signal = csd.beam_current[unique_mask]

    q_values = [e.atomic_number for e in elements]
    m_values = [e.atomic_mass for e in elements]

    sb = nonlinear_bounds
    lb = linear_bounds
    bounds = [lb] + [sb] * (polynomial_order - 1)
    resolving_power = 51
    sx, sy, lines, sigma = prepare_scoring(csd, signal_x, signal, elements,
                                           max_x, resolving_power)
    min_width = 1.5 * np.median(np.diff(sx))
    widths = np.maximum((lines + 1.0) / (2.355 * resolving_power), min_width)
    sol = opt.direct(
        make_residual(sx, sy, lines, 5*widths, max_x),
        bounds,
        maxfun=max_function_evaluations,
        maxiter=max_iterations,
        locally_biased=False,
        vol_tol=1e-16 / (10 ** (polynomial_order - 1)),
    )
    for factor in (2.0, 1.0):
        sol = opt.minimize(make_residual(sx, sy, lines, factor * widths, max_x),
                           sol.x, bounds=bounds, method="Nelder-Mead")
    poly = _make_polynomial(sol.x, max_x)
    fine_mq = np.linspace(0, max_x, 10000)
    fit_x_mapping = poly(fine_mq)
    x_to_mq_interp = np.interp(estimated_m_over_q, fit_x_mapping, fine_mq)
    return x_to_mq_interp + h_loc, sol
