"""Low-level CSV I/O helpers."""

from __future__ import annotations

import csv
import datetime
from pathlib import Path

from paranmr_synth.__version__ import __version__


def write_csv_rows_safe(
    *,
    file_name: str | Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
    comment: str | list[str] | None = None,
) -> None:
    """Write CSV rows with stable encoding and automatic parent-directory creation."""

    path = Path(file_name)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        handle.write(
            f"# This file was generated with paraNMR-Synth v{__version__} at {timestamp}\n"
        )
        if comment is not None:
            if isinstance(comment, str):
                handle.write(f"# {comment}\n")
            else:
                for line in comment:
                    handle.write(f"# {line}\n")
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
