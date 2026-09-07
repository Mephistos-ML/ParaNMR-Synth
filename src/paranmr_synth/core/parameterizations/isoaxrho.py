"""Iso/ax/rho-over-ax susceptibility parameterization."""

from __future__ import annotations

import numpy as np

from paranmr_synth.core.domain.samples import IsoAxRhoLatents
from paranmr_synth.core.domain.tensors import SusceptibilityTensor
from paranmr_synth.core.rotations.euler_zyz import build_zyz_rotation_matrix


def build_tensor_from_isoaxrho(latents: IsoAxRhoLatents) -> SusceptibilityTensor:
    """Build a full susceptibility tensor from iso/ax/rho-over-ax parameters."""

    chi_ax = latents.chi_ax
    rho_term = latents.rho_over_ax * chi_ax

    tensor_paf = np.array(
        [
            [-chi_ax / 3.0 + rho_term, 0.0, 0.0],
            [0.0, -chi_ax / 3.0 - rho_term, 0.0],
            [0.0, 0.0, 2.0 * chi_ax / 3.0],
        ],
        dtype=float,
    )
    tensor_paf += np.eye(3) * latents.chi_iso

    rotation = build_zyz_rotation_matrix(
        alpha_deg=latents.alpha_deg,
        beta_deg=latents.beta_deg,
        gamma_deg=latents.gamma_deg,
    )
    tensor = rotation @ tensor_paf @ rotation.T

    return SusceptibilityTensor(matrix_a3=tensor)
