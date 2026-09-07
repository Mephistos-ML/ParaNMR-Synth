"""ZYZ Euler rotation helpers."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def build_zyz_rotation_matrix(
    alpha_deg: float,
    beta_deg: float,
    gamma_deg: float,
) -> NDArray[np.float64]:
    """Return the ZYZ rotation matrix ``Rz(alpha) @ Ry(beta) @ Rz(gamma)``."""

    alpha = np.deg2rad(float(alpha_deg))
    beta = np.deg2rad(float(beta_deg))
    gamma = np.deg2rad(float(gamma_deg))

    cos_alpha, sin_alpha = np.cos(alpha), np.sin(alpha)
    cos_beta, sin_beta = np.cos(beta), np.sin(beta)
    cos_gamma, sin_gamma = np.cos(gamma), np.sin(gamma)

    rz_alpha = np.array(
        [
            [cos_alpha, -sin_alpha, 0.0],
            [sin_alpha, cos_alpha, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    ry_beta = np.array(
        [
            [cos_beta, 0.0, sin_beta],
            [0.0, 1.0, 0.0],
            [-sin_beta, 0.0, cos_beta],
        ],
        dtype=float,
    )
    rz_gamma = np.array(
        [
            [cos_gamma, -sin_gamma, 0.0],
            [sin_gamma, cos_gamma, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )

    return rz_alpha @ ry_beta @ rz_gamma
