"""Prepare ParaNMR molecular state for synthetic dataset generation."""

from __future__ import annotations

import hashlib

import numpy as np

from paranmr.app.loaders.paramag_centre_load import load_paramagnetic_centre
from paranmr.core.build.elstate import build_electronic_state
from paranmr.core.build.hfc import build_hfc_from_pdip
from paranmr.core.domain.mol import Molecule
from paranmr.tools.coords.xyz_fmt import add_label_indices, load_xyz

from paranmr_synth.cfg.dataset import DatasetGenerationConfig
from paranmr_synth.core.sampling import sample_diamagnetic_shifts


def prepare_dataset_molecule(config: DatasetGenerationConfig) -> tuple[Molecule, str]:
    """Load one geometry and attach ParaNMR-ready synthetic experiment state."""
    labels, coordinates = load_xyz(config.hyperfine_file)
    indexed_labels = add_label_indices(labels)
    molecule = Molecule.from_labels_coords(
        labels=indexed_labels,
        coords=coordinates,
        elements=config.nuclei_include,
    )
    load_paramagnetic_centre(molecule, list(config.paramagnetic_centre))
    molecule.electronic = build_electronic_state(
        spin_S=config.spin,
        orbit_L=config.orbit,
        total_J=config.total_momentum_j,
    )
    build_hfc_from_pdip(molecule)
    checksum = geometry_checksum(labels=tuple(molecule.labels), coordinates=molecule.coords)
    dia_shifts = sample_diamagnetic_shifts(
        atom_labels=tuple(nucleus.label for nucleus in molecule.nuclei),
        geometry_checksum=checksum,
        seed=config.seed,
        range_min_ppm=config.dia_range_min_ppm,
        range_max_ppm=config.dia_range_max_ppm,
    )
    for nucleus in molecule.nuclei:
        nucleus.shift.dia = dia_shifts[nucleus.label]
    return molecule, checksum


def geometry_checksum(*, labels: tuple[str, ...], coordinates: np.ndarray) -> str:
    """Return an order-independent checksum for labelled Cartesian geometry."""
    coordinate_array = np.asarray(coordinates, dtype=float)
    if coordinate_array.shape != (len(labels), 3):
        raise ValueError("coordinates must have shape (len(labels), 3)")
    records = sorted(
        f"{label}|{x:.12g}|{y:.12g}|{z:.12g}"
        for label, (x, y, z) in zip(labels, coordinate_array)
    )
    return hashlib.sha256("\n".join(records).encode("utf-8")).hexdigest()
