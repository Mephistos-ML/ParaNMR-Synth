"""Write atom-labelled diamagnetic-shift files."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd

from paranmr_synth.io.csv.csv_util import write_csv_safe


def write_diamagnetic(*, shifts: Mapping[str, float], output_file: Path) -> None:
    """Write ParaNMR-compatible atom-labelled diamagnetic shifts."""
    rows = [
        {"atom_label": label, "shift": shift} for label, shift in sorted(shifts.items())
    ]
    write_csv_safe(pd.DataFrame(rows, columns=["atom_label", "shift"]), output_file, float_format="%.15g")
