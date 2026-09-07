"""Deterministic susceptibility-latent generation."""

from __future__ import annotations

from dataclasses import dataclass

from paranmr_synth.cfg.dataset import DatasetGenerationConfig
from paranmr_synth.core.generators.deterministic import unit_interval_draw


@dataclass(frozen=True, slots=True)
class SusceptibilityLatents:
    """Sampled iso/ax/rho/Euler susceptibility parameters."""

    iso: float
    ax: float
    rho_over_ax: float
    alpha: float
    beta: float
    gamma: float


def generate_susceptibility_latents(
    *, config: DatasetGenerationConfig, geometry_checksum: str, case_index: int
) -> SusceptibilityLatents:
    """Generate deterministic susceptibility parameters for one case."""
    def draw(name: str, lower: float, upper: float) -> float:
        return lower + (upper - lower) * unit_interval_draw(
            config.seed, geometry_checksum, case_index, name
        )

    return SusceptibilityLatents(
        iso=draw("iso", config.susceptibility_iso.lower, config.susceptibility_iso.upper),
        ax=draw("ax", config.susceptibility_ax.lower, config.susceptibility_ax.upper),
        rho_over_ax=draw("rho_over_ax", config.susceptibility_rho_over_ax.lower, config.susceptibility_rho_over_ax.upper),
        alpha=draw("alpha", config.susceptibility_alpha.lower, config.susceptibility_alpha.upper),
        beta=draw("beta", config.susceptibility_beta.lower, config.susceptibility_beta.upper),
        gamma=draw("gamma", config.susceptibility_gamma.lower, config.susceptibility_gamma.upper),
    )
