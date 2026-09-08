"""Deterministic susceptibility-latent generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from paranmr_synth.core.generators.deterministic import unit_interval_draw
from paranmr.app.policies.susc import resolve_susc_fit_variables
from paranmr.core.phys.susc import get_spin_only_susc

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

    sampled_ax = draw(
        "ax", config.susceptibility.ax.lower, config.susceptibility.ax.upper
    )
    _, canonical = resolve_susc_fit_variables(
        raw_variables={"ax": ["fix", sampled_ax]},
        input_units=config.susceptibility.input_units,
        temperature=config.experiment.temperature_k,
        spin=config.hyperfine.spin,
    )
    return SusceptibilityLatents(
        iso=get_spin_only_susc(
            spin=config.hyperfine.spin,
            orbit=config.hyperfine.orbit,
            total_momentum_J=config.hyperfine.total_momentum_j,
            temperature=config.experiment.temperature_k,
        ),
        ax=canonical["ax"],
        rho_over_ax=draw("rho_over_ax", config.susceptibility.rho_over_ax.lower, config.susceptibility.rho_over_ax.upper),
        alpha=draw("alpha", config.susceptibility.alpha.lower, config.susceptibility.alpha.upper),
        beta=draw("beta", config.susceptibility.beta.lower, config.susceptibility.beta.upper),
        gamma=draw("gamma", config.susceptibility.gamma.lower, config.susceptibility.gamma.upper),
    )
