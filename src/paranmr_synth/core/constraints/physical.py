"""Physical and tensor-level validation rules."""

from __future__ import annotations

from typing import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


def as_symmetric_tensor(value: ArrayLike) -> NDArray[np.float64]:
    """Return a validated 3x3 symmetric tensor."""

    tensor = np.asarray(value, dtype=float)
    if tensor.shape != (3, 3):
        raise ValueError("Susceptibility tensor must have shape (3, 3).")
    if not np.allclose(tensor, tensor.T, atol=1e-10, rtol=0.0):
        raise ValueError("Susceptibility tensor must be symmetric.")
    return tensor


def validate_rho_over_ax(rho_over_ax: float) -> float:
    """Validate the iso-ax-rho rhombicity ratio."""

    value = float(rho_over_ax)
    if not 0.0 <= value <= 1.0 / 3.0:
        raise ValueError("IsoAxRhoLatents.rho_over_ax must satisfy 0 <= rho_over_ax <= 1/3.")
    return value


def validate_euler_zyz_angles_deg(
    alpha_deg: float,
    beta_deg: float,
    gamma_deg: float,
) -> tuple[float, float, float]:
    """Validate Euler angles in the zyz convention."""

    alpha = float(alpha_deg)
    beta = float(beta_deg)
    gamma = float(gamma_deg)

    if not 0.0 <= alpha <= 360.0:
        raise ValueError("IsoAxRhoLatents.alpha_deg must satisfy 0 <= alpha_deg <= 360.")
    if not 0.0 <= beta <= 180.0:
        raise ValueError("IsoAxRhoLatents.beta_deg must satisfy 0 <= beta_deg <= 180.")
    if not 0.0 <= gamma <= 360.0:
        raise ValueError("IsoAxRhoLatents.gamma_deg must satisfy 0 <= gamma_deg <= 360.")

    return alpha, beta, gamma


def validate_positive_temperature_k(temperature_k: float) -> float:
    """Validate one positive absolute temperature."""

    value = float(temperature_k)
    if value <= 0.0:
        raise ValueError("TensorPoint.temperature_k must be positive.")
    return value


def validate_strictly_increasing_temperatures(
    temperatures_k: Iterable[float],
) -> tuple[float, ...]:
    """Validate a temperature sequence with no duplicates."""

    values = tuple(float(value) for value in temperatures_k)
    if any(curr <= prev for prev, curr in zip(values, values[1:])):
        raise ValueError(
            "TensorSeries temperatures must be strictly increasing without duplicates."
        )
    return values
