"""Deterministic susceptibility-latent generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from paranmr_synth.core.generators.deterministic import unit_interval_draw
from paranmr.app.policies.susc import resolve_susc_fit_variables

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

    sampled = {
        "iso": draw("iso", config.susceptibility.iso.lower, config.susceptibility.iso.upper),
        "ax": draw("ax", config.susceptibility.ax.lower, config.susceptibility.ax.upper),
    }
    _, canonical = resolve_susc_fit_variables(
        raw_variables={name: ["fix", value] for name, value in sampled.items()},
        input_units=config.susceptibility.input_units,
        temperature=config.experiment.temperature_k,
        spin=config.hyperfine.spin,
    )
    return SusceptibilityLatents(
        iso=canonical["iso"],
        ax=canonical["ax"],
        rho_over_ax=draw("rho_over_ax", config.susceptibility.rho_over_ax.lower, config.susceptibility.rho_over_ax.upper),
        alpha=draw("alpha", config.susceptibility.alpha.lower, config.susceptibility.alpha.upper),
        beta=draw("beta", config.susceptibility.beta.lower, config.susceptibility.beta.upper),
        gamma=draw("gamma", config.susceptibility.gamma.lower, config.susceptibility.gamma.upper),
    )
