"""Generate susceptibility-tensor series and write them to disk."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from paranmr_synth.core.generators import (
    SeriesGeneratorSpec,
    generate_tensor_series_batch,
)
from paranmr_synth.io import write_paranmr_csv

logger = logging.getLogger(__name__)


def run_generate(
    spec: SeriesGeneratorSpec,
    *,
    output_dir: str | Path,
    seed: int | None = None,
    series_metadata: dict[str, str] | None = None,
) -> tuple[Path, ...]:
    """Generate a batch of tensor series and write each series to a CSV file."""

    logger.info("Generating %d tensor series", spec.n_series)
    rng = np.random.default_rng(seed)
    batch = generate_tensor_series_batch(spec, rng)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    for index, series in enumerate(batch, start=1):
        if series_metadata is not None:
            series.metadata.update(series_metadata)
        file_path = output_path / _build_series_file_name(index, series)
        write_paranmr_csv(series, file_path)
        written_files.append(file_path)

    logger.info("Generation output written to %s", str(output_path))
    return tuple(written_files)


def _build_series_file_name(index: int, series) -> str:
    temperatures_k = tuple(point.temperature_k for point in series.points)
    start_k = _format_temperature_token(temperatures_k[0])
    stop_k = _format_temperature_token(temperatures_k[-1])
    if start_k == stop_k:
        return f"susceptibility_tensor_{index}_{start_k}.csv"
    return f"susceptibility_tensor_{index}_{start_k}_to_{stop_k}.csv"


def _format_temperature_token(temperature_k: float) -> str:
    rounded = round(temperature_k)
    if abs(temperature_k - rounded) < 1e-9:
        return f"{rounded}K"
    return f"{temperature_k:g}K"
