import numpy as np
import pytest

from paranmr_synth.core.constraints import (
    as_symmetric_tensor,
    validate_euler_zyz_angles_deg,
    validate_rho_over_ax,
    validate_strictly_increasing_temperatures,
)


def test_validate_rho_over_ax_accepts_closed_interval() -> None:
    assert validate_rho_over_ax(0.0) == 0.0
    assert validate_rho_over_ax(1.0 / 3.0) == 1.0 / 3.0


def test_validate_euler_zyz_angles_deg_rejects_out_of_range_beta() -> None:
    with pytest.raises(ValueError, match="beta_deg"):
        validate_euler_zyz_angles_deg(0.0, 181.0, 0.0)


def test_validate_strictly_increasing_temperatures_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_strictly_increasing_temperatures((280.0, 280.0, 281.0))


def test_as_symmetric_tensor_rejects_nonsymmetric_matrix() -> None:
    with pytest.raises(ValueError, match="symmetric"):
        as_symmetric_tensor(np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]))
