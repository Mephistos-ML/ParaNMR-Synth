"""Acceptance test for the synthetic case → ParaNMR fit → validation loop."""

from __future__ import annotations

import os
import csv
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from paranmr_synth.app.pipelines.dataset_export import generate_dataset
from paranmr_synth.app.pipelines.dataset_validation import validate_dataset_case
from paranmr_synth.cfg.dataset import DatasetGenerationConfig


@pytest.mark.integration
def test_controlled_synthetic_case_recovers_chi_and_linewidth(tmp_path: Path):
    """Recover one active χ degree of freedom through the real ParaNMR CLI.

    The control profile fixes nuisance susceptibility coordinates. It verifies
    the file contract and numerical round-trip without asserting that one
    spectrum identifies every ``isoaxrho_euler`` degree of freedom.
    """
    if shutil.which("paranmr") is None:
        pytest.skip("ParaNMR CLI is not installed")
    geometry = tmp_path / "model.xyz"
    geometry.write_text(
        "3\nsynthetic Yb model\nYb 0 0 0\nH 1 0 0\nH 2 0 0\n",
        encoding="utf-8",
    )
    config = DatasetGenerationConfig.from_mapping(
        {
            "project": {"name": "control", "n_cases": 1, "seed": 42},
            "hyperfine": {
                "method": "pdip", "file": str(geometry),
                "paramagnetic_centre": [0, 0, 0], "spin": 0.5,
                "orbit": 3, "total_momentum_J": 3.5,
            },
            "nuclei": {"include": "H"},
            "diamagnetic": {"range_min_ppm": 0, "range_max_ppm": 10},
            "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7},
            "moments": {"number_of_moments": 6},
            "linewidth": {
                "method": "r6",
                "variables": {"p1": [705.05, 705.05], "p2": [0.25, 0.25]},
            },
            "susceptibility": {
                "model": "isoaxrho_euler",
                "variables": {
                    "iso": [0, 0], "ax": [0.01, 0.01],
                    "rho_over_ax": [0.1, 0.1], "alpha": [0, 0],
                    "beta": [0, 0], "gamma": [0, 0],
                },
            },
        }
    )
    root = generate_dataset(config=config, output_dir=tmp_path / "output")
    case_dir = next((root / "cases").iterdir())
    fit_dir = case_dir / "fit"
    _fix_control_nuisance_variables(fit_dir / "config.yml")
    environment = {**os.environ, "MPLBACKEND": "Agg", "MPLCONFIGDIR": str(tmp_path / "mpl")}
    result = subprocess.run(
        [
            "paranmr", "--hide", "fit_susc", "config.yml",
            "--shift_plots", "off", "--spread_plots", "off",
            "--contrib_plots", "off", "--isoaxrho_plots", "off",
        ],
        cwd=fit_dir,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    truth = _read_one_row(case_dir / "synthetic_output" / "susceptibility.csv")
    fitted = _read_one_row(
        fit_dir / "paranmr_fitted_output" / "susceptibility_tensor.csv"
    )
    fitted_columns = {
        "chi_xx": "chi_xx (Å^3)", "chi_xy": "chi_xy (Å^3)",
        "chi_xz": "chi_xz (Å^3)", "chi_yy": "chi_yy (Å^3)",
        "chi_yz": "chi_yz (Å^3)", "chi_zz": "chi_zz (Å^3)",
    }
    for name, column in fitted_columns.items():
        assert abs(float(fitted[column]) - float(truth[name])) <= 5e-7
    report = yaml.safe_load(
        validate_dataset_case(case_dir).read_text(encoding="utf-8")
    )
    assert report["moment_score"] is None
    assert report["absolute_error"]["linewidth_p1"] <= 1e-9
    assert report["absolute_error"]["linewidth_p2"] <= 1e-9


def _fix_control_nuisance_variables(config_file: Path) -> None:
    """Make a deliberately identifiable one-parameter recovery control."""
    payload = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    variables = payload["susc_fit"]["variables"]
    for name in ("iso", "rho_over_ax", "alpha", "beta", "gamma"):
        variables[name][0] = "fix"
    config_file.write_text(
        yaml.safe_dump(payload, sort_keys=False), encoding="utf-8"
    )


def _read_one_row(file_name: Path) -> dict[str, str]:
    with file_name.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
    assert len(rows) == 1
    return rows[0]
