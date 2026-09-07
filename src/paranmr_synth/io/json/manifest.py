"""Write dataset provenance manifests."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from paranmr.__version__ import __version__ as paranmr_version

from paranmr_synth.__version__ import __version__

if TYPE_CHECKING:
    from paranmr_synth.cfg.dataset import DatasetGenerationConfig


def write_manifest(
    *, config: DatasetGenerationConfig, output_file: Path, geometry_checksum: str
) -> None:
    """Write the full provenance contract for a generated dataset."""
    payload = {
        "schema_version": 1,
        "generator": {
            "name": "ParaNMR-Synth",
            "version": __version__,
            "paranmr_version": paranmr_version,
        },
        "project_name": config.project.name,
        "seed": config.project.seed,
        "n_cases": config.project.n_cases,
        "number_of_moments": config.number_of_moments,
        "geometry_checksum": geometry_checksum,
        "normalized_config": asdict(config),
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
