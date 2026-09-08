"""Write ParaNMR fixed-assignment fit configurations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from paranmr_synth.cfg.dataset import DatasetGenerationConfig


def write_fit_config(*, config: DatasetGenerationConfig, output_file: Path) -> None:
    """Write the self-contained ParaNMR replay configuration."""
    payload = {
        "project": {"name": "paranmr_fitted_output"},
        "hyperfine": {
            "method": "pdip", "file": "geometry.xyz",
            "paramagnetic_centre": list(config.hyperfine.paramagnetic_centre),
            "spin": config.hyperfine.spin, "orbit": config.hyperfine.orbit,
            "total_momentum_J": config.hyperfine.total_momentum_j,
        },
        "nuclei": {"include": config.nuclei_include},
        "diamagnetic": {
            "method": config.diamagnetic.method,
            "file": _replay_input_name("diamagnetic_input", config.diamagnetic.file),
        },
        "experiment": {"files": "generated_shifts.csv"},
        "assignment": {"method": "fixed"},
        "linewidth": {"method": "experimental", "estimate": "p1_p2"},
        "susc_fit": {
            "type": "isoaxrho_euler",
            "variables": {
                "iso": ["fit", 0.0], "ax": ["fit", 0.01], "rho_over_ax": ["fit", 0.1],
                "alpha": ["fit", 0.0], "beta": ["fit", 0.0], "gamma": ["fit", 0.0],
            },
        },
    }
    if config.diamagnetic.reference_file:
        payload["diamagnetic_ref"] = {
            "method": config.diamagnetic.reference_method,
            "file": _replay_input_name(
                "diamagnetic_reference_input", config.diamagnetic.reference_file
            ),
        }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)


def _replay_input_name(prefix: str, source_file: str) -> str:
    """Return the replay filename used by the paired dataset exporter."""
    return prefix + Path(source_file).suffix
