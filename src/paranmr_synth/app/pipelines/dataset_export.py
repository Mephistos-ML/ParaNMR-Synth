"""Orchestrate a complete replayable synthetic dataset export."""

from __future__ import annotations

from pathlib import Path
import shutil

from paranmr_synth.app.pipelines.dataset_generation import (
    GeneratedCase,
    generate_case_artifacts,
    prepare_dataset_molecule,
)
from paranmr_synth.cfg.dataset import DatasetGenerationConfig
from paranmr_synth.io.csv.experiment import write_experiment
from paranmr_synth.io.csv.linewidth import write_linewidth
from paranmr_synth.io.csv.ml import write_ml_dataset
from paranmr_synth.io.csv.susceptibility import write_susceptibility
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
        _write_case(config=config, case=case, root=root)
    write_ml_dataset(cases=cases, config=config, output_file=root / "dataset.csv")
    write_manifest(
        config=config,
        output_file=root / "manifest.json",
        geometry_checksum=checksum,
    )
    return root


def _write_case(*, config: DatasetGenerationConfig, case: GeneratedCase, root: Path) -> None:
    """Write one replayable case through format-specific IO writers."""
    case_root = root / "cases" / case.record.sample_id
    fit_dir = case_root / "fit"
    truth_dir = case_root / "synthetic_output"
    write_indexed_geometry(input_file=config.hyperfine.file, output_file=fit_dir / "geometry.xyz")
    write_fit_config(config=config, output_file=fit_dir / "config.yml")
    write_experiment(config=config, case=case, output_file=fit_dir / "generated_shifts.csv")
    _copy_diamagnetic_inputs(config=config, output_directory=fit_dir)
    write_susceptibility(
        target=case.record.target,
        latent=case.susceptibility,
        config=config,
        output_file=truth_dir / "susceptibility.csv",
    )
    write_linewidth(latent=case.linewidth, output_file=truth_dir / "linewidth.csv")


def _copy_diamagnetic_inputs(
    *, config: DatasetGenerationConfig, output_directory: Path
) -> None:
    """Copy source diamagnetic inputs for self-contained ParaNMR replay."""
    dia_name = _replay_input_name("diamagnetic_input", config.diamagnetic.file)
    shutil.copy2(config.diamagnetic.file, output_directory / dia_name)
    if config.diamagnetic.reference_file:
        shutil.copy2(
            config.diamagnetic.reference_file,
            output_directory / _replay_input_name(
                "diamagnetic_reference_input", config.diamagnetic.reference_file
            ),
        )


def _replay_input_name(prefix: str, source_file: str) -> str:
    """Return a stable replay filename retaining the source suffix."""
    return prefix + Path(source_file).suffix
