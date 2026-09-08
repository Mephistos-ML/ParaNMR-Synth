"""Write synthetic susceptibility truth."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from paranmr_synth.io.csv.csv_util import write_csv_safe

if TYPE_CHECKING:
    from paranmr_synth.core.dataset.records import TensorTarget
    from paranmr_synth.core.generators.susceptibility import SusceptibilityLatents


def write_susceptibility(
    *, target: TensorTarget, latent: SusceptibilityLatents, output_file: Path
) -> None:
    """Write Cartesian χ and its sampled parameterization."""
    row = {
        **target.as_row(),
        "chi_iso": latent.iso,
        "chi_ax": latent.ax,
        "chi_rh": latent.ax * latent.rho_over_ax,
        "rh_over_ax": latent.rho_over_ax,
        "alpha": latent.alpha,
        "beta": latent.beta,
        "gamma": latent.gamma,
    }
    write_csv_safe(pd.DataFrame([row]), output_file, float_format="%.15g")
