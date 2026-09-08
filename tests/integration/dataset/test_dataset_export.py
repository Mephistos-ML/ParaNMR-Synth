import csv
import json
from pathlib import Path

from paranmr.cfg.config import FitSuscConfig

from paranmr_synth.app.pipelines.dataset_export import generate_dataset
from paranmr_synth.cfg.dataset import DatasetGenerationConfig


def test_generate_dataset_writes_replayable_cases_and_paired_ml_table(tmp_path: Path):
    geometry = tmp_path / "model.xyz"
    geometry.write_text(
        "3\nsynthetic Yb model\nYb 0 0 0\nH 1 0 0\nH 0 1 0\n",
        encoding="utf-8",
    )
    config = DatasetGenerationConfig.from_mapping(
        {
            "project": {"name": "yb", "n_cases": 2, "seed": 42},
            "hyperfine": {
                "method": "pdip", "file": str(geometry),
                "paramagnetic_centre": [0, 0, 0], "spin": 0.5,
                "orbit": 3, "total_momentum_J": 3.5,
            },
            "nuclei": {"include": "H"},
            "diamagnetic": {"range_min_ppm": 0, "range_max_ppm": 10},
            "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7},
            "moments": {"number_of_moments": 3},
            "linewidth": {"method": "r6", "variables": {"p1": [500, 2000], "p2": [0, 1]}},
            "susceptibility": {"model": "isoaxrho_euler"},
        }
    )

    root = generate_dataset(config=config, output_dir=tmp_path / "output")

    with (root / "dataset.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
    assert len(rows) == 2
    assert set(rows[0]) == {
        "sample_id", "m1", "m2", "m3", "chi_xx", "chi_xy", "chi_xz",
        "chi_yy", "chi_yz", "chi_zz", "linewidth_p1", "linewidth_p2",
    }
    case_root = root / "cases" / rows[0]["sample_id"]
    fit_config = case_root / "fit" / "config.yml"
    assert fit_config.is_file()
    assert (case_root / "fit" / "geometry.xyz").is_file()
    assert (case_root / "fit" / "generated_shifts.csv").is_file()
    assert (case_root / "fit" / "diamagnetic.csv").is_file()
    assert (case_root / "synthetic_output" / "susceptibility.csv").is_file()
    assert (case_root / "synthetic_output" / "linewidth.csv").is_file()
    csv_artifacts = [
        root / "dataset.csv",
        case_root / "fit" / "generated_shifts.csv",
        case_root / "fit" / "diamagnetic.csv",
        case_root / "synthetic_output" / "susceptibility.csv",
        case_root / "synthetic_output" / "linewidth.csv",
    ]
    for artifact in csv_artifacts:
        assert artifact.read_text(encoding="utf-8-sig").startswith(
            "# This file was generated with ParaNMR-Synth v"
        )
    assert "paranmr_fitted_output" in fit_config.read_text()
    assert FitSuscConfig.from_file(fit_config).assignment_method == "fixed"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["normalized_config"]["number_of_moments"] == 3
    assert "paranmr_version" in manifest["generator"]


def test_fixed_profile_exports_paranmr_r6_linewidth_estimation(tmp_path: Path):
    geometry = tmp_path / "model.xyz"
    geometry.write_text(
        "3\nsynthetic Yb model\nYb 0 0 0\nH 1 0 0\nH 0 1 0\n",
        encoding="utf-8",
    )
    config = DatasetGenerationConfig.from_mapping(
        {
            "project": {"name": "yb", "n_cases": 1, "seed": 42},
            "hyperfine": {"method": "pdip", "file": str(geometry), "paramagnetic_centre": [0, 0, 0], "spin": 0.5, "orbit": 3, "total_momentum_J": 3.5},
            "nuclei": {"include": "H"}, "diamagnetic": {"range_min_ppm": 0, "range_max_ppm": 10},
            "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7}, "moments": {"number_of_moments": 3},
            "linewidth": {"method": "r6", "variables": {"p1": [705.05, 705.05], "p2": [0.25, 0.25]}},
            "susceptibility": {"model": "isoaxrho_euler"},
        }
    )

    root = generate_dataset(config=config, output_dir=tmp_path / "output")
    fit_config = next((root / "cases").glob("*/fit/config.yml"))

    parsed = FitSuscConfig.from_file(fit_config)
    assert parsed.linewidth_method == "experimental"
    assert parsed.linewidth_estimate == "p1_p2"
