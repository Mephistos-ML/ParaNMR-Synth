"""Deterministic susceptibility-latent generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from paranmr.core.phys.susc import get_spin_only_susc
from paranmr_synth.core.generators.deterministic import unit_interval_draw

if TYPE_CHECKING:
    from paranmr_synth.cfg.dataset import DatasetGenerationConfig


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
    *, config: "DatasetGenerationConfig", geometry_checksum: str, case_index: int
) -> SusceptibilityLatents:
    """Generate deterministic susceptibility parameters for one case."""
    def draw(name: str, lower: float, upper: float) -> float:
        return lower + (upper - lower) * unit_interval_draw(
            config.project.seed, geometry_checksum, case_index, name
        )

    iso = get_spin_only_susc(
        spin=config.hyperfine.spin,
        orbit=config.hyperfine.orbit,
        total_momentum_J=config.hyperfine.total_momentum_j,
        temperature=config.experiment.temperature_k,
    )
    rho_over_ax = draw("rho_over_ax", 0.0, 1.0 / 3.0)
    ax_lower, ax_upper = _ax_bounds(iso=iso, rho_over_ax=rho_over_ax)
    return SusceptibilityLatents(
        iso=iso,
        ax=draw("ax", ax_lower, ax_upper),
        rho_over_ax=rho_over_ax,
        alpha=draw("alpha", 0.0, 360.0),
        beta=draw("beta", 0.0, 180.0),
        gamma=draw("gamma", 0.0, 360.0),
    )


def _ax_bounds(*, iso: float, rho_over_ax: float) -> tuple[float, float]:
    """Return axiality bounds that keep all principal χ components non-negative."""
    return -1.5 * iso, iso / (rho_over_ax + 1.0 / 3.0)
