"""Iso/ax/rho-over-ax susceptibility parameterization."""

from __future__ import annotations

from paranmr.core.fitting.susceptibility.models.isoaxrho_euler import (
    IsoAxRhoEulerFitter,
)

from paranmr_synth.core.domain.samples import IsoAxRhoLatents
from paranmr_synth.core.domain.tensors import SusceptibilityTensor


def build_tensor_from_isoaxrho(latents: IsoAxRhoLatents) -> SusceptibilityTensor:
    """Build a full susceptibility tensor from iso/ax/rho-over-ax parameters."""

    tensor = IsoAxRhoEulerFitter.totensor(
        {
            "iso": latents.chi_iso,
            "ax": latents.chi_ax,
            "rho_over_ax": latents.rho_over_ax,
            "alpha": latents.alpha_deg,
            "beta": latents.beta_deg,
            "gamma": latents.gamma_deg,
        }
    )
    return SusceptibilityTensor(matrix_a3=tensor)
