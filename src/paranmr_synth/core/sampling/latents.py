"""Deterministic susceptibility and linewidth latent sampling."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from paranmr_synth.cfg.dataset import DatasetGenerationConfig
from paranmr_synth.core.generators import ParameterSpec


@dataclass(frozen=True, slots=True)
class SampledLatents:
    """One complete χ and R6 linewidth latent state."""

    iso: float
    ax: float
    rho_over_ax: float
    alpha: float
    beta: float
    gamma: float
    p1: float
    p2: float


def sample_latents(
    *, config: DatasetGenerationConfig, geometry_checksum: str, case_index: int
) -> SampledLatents:
    """Sample one deterministic χ and linewidth state for a dataset case."""
    if case_index < 0:
        raise ValueError("case_index must be non-negative")

    def draw(name: str, spec: ParameterSpec) -> float:
        payload = f"{config.seed}|{geometry_checksum}|{case_index}|{name}".encode()
        value = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
        unit = value / float((1 << 64) - 1)
        return spec.lower + (spec.upper - spec.lower) * unit

    return SampledLatents(
        iso=draw("iso", config.susceptibility_iso),
        ax=draw("ax", config.susceptibility_ax),
        rho_over_ax=draw("rho_over_ax", config.susceptibility_rho_over_ax),
        alpha=draw("alpha", config.susceptibility_alpha),
        beta=draw("beta", config.susceptibility_beta),
        gamma=draw("gamma", config.susceptibility_gamma),
        p1=draw("p1", config.linewidth_p1),
        p2=draw("p2", config.linewidth_p2),
    )
