"""Write synthetic susceptibility truth."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from paranmr_synth.io.csv.csv_util import write_csv_safe

if TYPE_CHECKING:
    from paranmr_synth.core.dataset.records import TensorTarget
    from paranmr_synth.core.generators.susceptibility import SusceptibilityLatents
    from paranmr_synth.cfg.dataset import DatasetGenerationConfig


def write_susceptibility(
    *, target: TensorTarget, latent: SusceptibilityLatents, config: DatasetGenerationConfig, output_file: Path
) -> None:
    """Write Cartesian χ and its sampled parameterization."""
    from paranmr.app.policies.susc import resolve_susc_fit_variables
    _, fixed = resolve_susc_fit_variables(raw_variables={"iso": ["fix", 1.0]}, input_units=config.susceptibility.input_units, temperature=config.experiment.temperature_k, spin=config.hyperfine.spin)
    scale = fixed["iso"]
    row = {
        **{key: value / scale for key, value in target.as_row().items() if key.startswith("chi_")},
        "iso": latent.iso / scale,
        "ax": latent.ax / scale,
        "rho_over_ax": latent.rho_over_ax,
        "alpha": latent.alpha,
        "beta": latent.beta,
        "gamma": latent.gamma,
    }
    write_csv_safe(pd.DataFrame([row]), output_file, float_format="%.15g")
