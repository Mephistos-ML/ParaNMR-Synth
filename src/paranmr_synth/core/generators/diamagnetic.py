"""Deterministic synthetic diamagnetic-shift generation."""

from __future__ import annotations

from paranmr_synth.core.generators.deterministic import unit_interval_draw


def generate_diamagnetic_shifts(
    *, atom_labels: tuple[str, ...], geometry_checksum: str, seed: int,
    range_min_ppm: float, range_max_ppm: float
) -> dict[str, float]:
    """Generate one reproducible diamagnetic shift for each selected atom."""
    if range_min_ppm > range_max_ppm:
        raise ValueError("range_min_ppm must not exceed range_max_ppm")
    if len(set(atom_labels)) != len(atom_labels):
        raise ValueError("atom_labels must be unique")
    if not geometry_checksum:
        raise ValueError("geometry_checksum must be non-empty")
    return {
        label: float(range_min_ppm)
        + (float(range_max_ppm) - float(range_min_ppm))
        * unit_interval_draw(seed, geometry_checksum, "dia", label)
        for label in sorted(atom_labels)
    }
