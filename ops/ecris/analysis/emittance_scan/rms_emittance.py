from dataclasses import dataclass

import numpy as np

from ops.ecris.analysis.model.emittance_scan import EmittanceScan
from ops.ecris.devices.motor_controller_specification import Axis


@dataclass
class RMSEmittance:
    data: np.ndarray
    axis: Axis
    x: np.ndarray
    xp: np.ndarray
    x_mean: float
    xp_mean: float
    alpha: float
    beta: float
    gamma: float
    e_rms: float


def calculate_rms_emittance(emittance_scan: EmittanceScan) -> RMSEmittance:
    x = emittance_scan.position_range
    xp = emittance_scan.divergence_range
    axis = emittance_scan.scan_parameters.axis

    data = emittance_scan.data
    if data.shape != (len(x), len(xp)):
        data = data.T
        if data.shape != (len(x), len(xp)):
            raise RuntimeError

    x_mean = np.einsum("ij,i->", data, x * 1e-3) / np.sum(data)
    xp_mean = np.einsum("ij,j->", data, xp * 1e-3) / np.sum(data)
    x_var = x * 1e-3 - x_mean
    xp_var = xp * 1e-3 - xp_mean
    sigma_x_2 = np.sum(np.einsum("ij,i->j", data, np.power(x_var, 2))) / np.sum(data)
    sigma_xp_2 = np.sum(np.einsum("ij,j->i", data, np.power(xp_var, 2))) / np.sum(data)
    sigma_xxp = np.sum(np.einsum("i,i->", np.einsum("ij,j->i", data, xp_var), x_var)) / np.sum(
        data
    )
    e_rms = np.sqrt(sigma_x_2 * sigma_xp_2 - np.power(sigma_xxp, 2))
    alpha = -sigma_xxp / e_rms
    beta = sigma_x_2 / e_rms
    gamma = sigma_xp_2 / e_rms
    return RMSEmittance(data, axis, x, xp, x_mean, xp_mean, alpha, beta, gamma, e_rms)
