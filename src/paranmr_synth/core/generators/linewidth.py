"""Deterministic R6 linewidth-parameter generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from paranmr_synth.core.generators.deterministic import unit_interval_draw

if TYPE_CHECKING:
    from paranmr_synth.cfg.dataset import DatasetGenerationConfig


@dataclass(frozen=True, slots=True)
class LinewidthLatents:
    """Sampled global R6 linewidth parameters."""

    p1: float
    p2: float


def generate_linewidth_latents(
    *, config: "DatasetGenerationConfig", geometry_checksum: str, case_index: int
) -> LinewidthLatents:
    """Generate deterministic R6 linewidth parameters for one case."""
    def draw(name: str, lower: float, upper: float) -> float:
        return lower + (upper - lower) * unit_interval_draw(
            config.project.seed, geometry_checksum, case_index, name
        )

    return LinewidthLatents(
        p1=draw("p1", config.linewidth.p1.lower, config.linewidth.p1.upper),
        p2=draw("p2", config.linewidth.p2.lower, config.linewidth.p2.upper),
    )
