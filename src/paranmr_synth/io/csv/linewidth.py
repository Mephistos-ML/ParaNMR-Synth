"""Write synthetic linewidth truth."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from paranmr_synth.io.csv.csv_util import write_csv_safe

if TYPE_CHECKING:
    from paranmr_synth.core.generators.linewidth import LinewidthLatents


def write_linewidth(*, latent: LinewidthLatents, output_file: Path) -> None:
    """Write R6 linewidth parameters for synthetic-truth comparison."""
    write_csv_safe(
        pd.DataFrame([{"method": "r6", "p1": latent.p1, "p2": latent.p2}]),
        output_file,
        float_format="%.15g",
    )
