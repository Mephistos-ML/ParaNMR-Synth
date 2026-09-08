"""Orchestrate a complete replayable synthetic dataset export."""

from __future__ import annotations

from pathlib import Path
import shutil

import pandas as pd

from paranmr_synth.app.pipelines.dataset_generation import (
    GeneratedCase,
    generate_case_artifacts,
    prepare_dataset_molecule,
)
from paranmr_synth.cfg.dataset import DatasetGenerationConfig
from paranmr_synth.io.csv.experiment import write_experiment
from paranmr_synth.io.csv.ml import write_ml_dataset
from paranmr_synth.io.csv.susceptibility import write_susceptibility
from paranmr_synth.io.csv.csv_util import write_csv_safe
from paranmr_synth.io.json.manifest import write_manifest
from paranmr_synth.io.xyz.geometry import write_indexed_geometry
from paranmr_synth.io.yaml.fit import write_fit_config


def generate_dataset(
    *, config: DatasetGenerationConfig, output_dir: str | Path
) -> Path:
    """Generate all cases, their ParaNMR inputs, and the paired ML dataset."""
    molecule, checksum = prepare_dataset_molecule(config)
    cases = tuple(
        generate_case_artifacts(
            config=config,
            molecule=molecule,
            geometry_checksum=checksum,
            case_index=index,
        )
        for index in range(config.project.n_cases)
    )
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    for case in cases:
        _write_case(config=config, case=case, molecule=molecule, root=root)
    write_ml_dataset(cases=cases, output_file=root / "dataset.csv")
    write_manifest(
        config=config,
        output_file=root / "manifest.json",
        geometry_checksum=checksum,
    )
    return root


def _write_case(*, config: DatasetGenerationConfig, case: GeneratedCase, molecule, root: Path) -> None:
    """Write one replayable case through format-specific IO writers."""
    case_root = root / "cases" / case.record.sample_id
    data_dir = case_root / "DATA"
    fitting_dir = case_root / "SIMULATIONS" / "FITTING"
    write_indexed_geometry(input_file=config.hyperfine.file, output_file=data_dir / "HFC" / "geometry.xyz")
    if config.signal_labels_file:
        labels_file = data_dir / "LABELS" / "labels.csv"
        labels_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config.signal_labels_file, labels_file)
    write_fit_config(config=config, output_file=fitting_dir / "config.yml")
    write_experiment(config=config, case=case, output_file=data_dir / "PARA" / "generated_shifts.csv")
    _write_diamagnetic_csv(molecule=molecule, output_file=data_dir / "DIA" / "diamagnetic.csv")
    write_susceptibility(
        target=case.record.target,
        latent=case.susceptibility,
        output_file=data_dir / "CHI" / "susceptibility.csv",
    )


def _write_diamagnetic_csv(*, molecule, output_file: Path) -> None:
    """Write ParaNMR-normalized atom-resolved dia shifts for replay."""
    write_csv_safe(
        pd.DataFrame(
            [{"atom_label": nucleus.label, "shift": nucleus.shift.dia} for nucleus in molecule.nuclei]
        ),
        output_file,
        float_format="%.15g",
    )
