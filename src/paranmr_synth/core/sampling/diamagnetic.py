"""Deterministic synthetic diamagnetic-shift sampling."""

from __future__ import annotations

import hashlib


def sample_diamagnetic_shifts(
    *,
    atom_labels: tuple[str, ...],
    geometry_checksum: str,
    seed: int,
    range_min_ppm: float,
    range_max_ppm: float,
) -> dict[str, float]:
    """Sample one reproducible diamagnetic shift for each selected atom.

    The draw for each atom is derived independently from the project seed,
    geometry checksum, and atom label. Therefore reordering an XYZ file cannot
    change the value assigned to an atom with the same label.

    Args:
        atom_labels: Unique selected atom labels.
        geometry_checksum: Stable checksum of the source geometry.
        seed: Dataset-level random seed.
        range_min_ppm: Inclusive lower shift bound in ppm.
        range_max_ppm: Inclusive upper shift bound in ppm.

    Returns:
        Mapping from atom label to generated diamagnetic shift in ppm.
    """
    if range_min_ppm > range_max_ppm:
        raise ValueError("range_min_ppm must not exceed range_max_ppm")
    if len(set(atom_labels)) != len(atom_labels):
        raise ValueError("atom_labels must be unique")
    if not geometry_checksum:
        raise ValueError("geometry_checksum must be non-empty")
    minimum = float(range_min_ppm)
    maximum = float(range_max_ppm)
    return {
        label: minimum + (maximum - minimum) * _unit_interval_draw(
            seed=seed,
            geometry_checksum=geometry_checksum,
            atom_label=label,
        )
        for label in sorted(atom_labels)
    }


def _unit_interval_draw(*, seed: int, geometry_checksum: str, atom_label: str) -> float:
    payload = f"{seed}|{geometry_checksum}|{atom_label}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    numerator = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return numerator / float((1 << 64) - 1)
