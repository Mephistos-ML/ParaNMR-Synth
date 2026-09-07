import numpy as np

from paranmr_synth.core.domain import IsoAxRhoLatents
from paranmr_synth.core.parameterizations import build_tensor_from_isoaxrho


def test_build_tensor_from_isoaxrho_without_rotation_returns_diagonal_tensor():
    latents = IsoAxRhoLatents(
        chi_iso=10.0,
        chi_ax=3.0,
        rho_over_ax=1.0 / 6.0,
        alpha_deg=0.0,
        beta_deg=0.0,
        gamma_deg=0.0,
    )

    tensor = build_tensor_from_isoaxrho(latents)

    expected = np.array(
        [
            [9.5, 0.0, 0.0],
            [0.0, 8.5, 0.0],
            [0.0, 0.0, 12.0],
        ],
        dtype=float,
    )
    assert np.allclose(tensor.matrix_a3, expected)
    assert tensor.chi_iso == 10.0


def test_build_tensor_from_isoaxrho_with_rotation_returns_symmetric_full_tensor():
    latents = IsoAxRhoLatents(
        chi_iso=10.0,
        chi_ax=3.0,
        rho_over_ax=1.0 / 6.0,
        alpha_deg=30.0,
        beta_deg=45.0,
        gamma_deg=60.0,
    )

    tensor = build_tensor_from_isoaxrho(latents)

    assert np.allclose(tensor.matrix_a3, tensor.matrix_a3.T)
    assert np.isclose(tensor.chi_iso, 10.0)
    assert not np.allclose(tensor.matrix_a3, np.diag(np.diag(tensor.matrix_a3)))
