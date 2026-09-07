"""Write paired supervised-learning tables."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from paranmr_synth.io.csv.csv_util import write_csv_safe

if TYPE_CHECKING:
    from paranmr_synth.app.pipelines.dataset_generation import GeneratedCase
    from paranmr_synth.cfg.dataset import DatasetGenerationConfig


def write_ml_dataset(*, cases: tuple[GeneratedCase, ...], config: DatasetGenerationConfig, output_file: Path) -> None:
    """Write the canonical paired moments-to-parameters ML table."""
    scale = _scale_to_a3(config)
    rows = [
        {"sample_id": case.record.sample_id, **case.record.moments, **_scaled_target(case.record.target.as_row(), scale)}
        for case in cases
    ]
    write_csv_safe(pd.DataFrame(rows), output_file, float_format="%.15g")


def _scale_to_a3(config: DatasetGenerationConfig) -> float:
    from paranmr.app.policies.susc import resolve_susc_fit_variables
    _, fixed = resolve_susc_fit_variables(raw_variables={"iso": ["fix", 1.0]}, input_units=config.susceptibility.input_units, temperature=config.experiment.temperature_k, spin=config.hyperfine.spin)
    return fixed["iso"]


def _scaled_target(target: dict[str, float], scale: float) -> dict[str, float]:
    return {name: value / scale if name.startswith("chi_") else value for name, value in target.items()}
