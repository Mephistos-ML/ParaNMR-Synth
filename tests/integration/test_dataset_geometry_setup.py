from pathlib import Path

from paranmr_synth.app.pipelines import prepare_dataset_molecule
from paranmr_synth.cfg import DatasetGenerationConfig


def test_prepare_dataset_molecule_attaches_pdip_and_diamagnetic_shifts(tmp_path: Path):
    geometry = tmp_path / "model.xyz"
    geometry.write_text(
        "3\nsynthetic Yb model\nYb 0.0 0.0 0.0\nH 1.0 0.0 0.0\nH 0.0 1.0 0.0\n",
        encoding="utf-8",
    )
    config = DatasetGenerationConfig.from_mapping(
        {
            "project": {"name": "test", "n_cases": 1, "seed": 42},
            "hyperfine": {
                "method": "pdip",
                "file": str(geometry),
                "paramagnetic_centre": [0.0, 0.0, 0.0],
                "spin": 0.5,
                "orbit": 3,
                "total_momentum_J": 3.5,
            },
            "nuclei": {"include": "H"},
            "diamagnetic": {"range_min_ppm": 0.0, "range_max_ppm": 10.0},
            "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7},
            "moments": {"number_of_moments": 10},
            "linewidth": {"method": "r6", "variables": {"p1": [500, 2000], "p2": [0, 1]}},
            "susceptibility": {"model": "isoaxrho_euler", "variables": {"iso": [0, 0.02], "ax": [-0.08, 0.08], "rho_over_ax": [0, 1 / 3], "alpha": [0, 360], "beta": [0, 180], "gamma": [0, 360]}},
        }
    )

    molecule, checksum = prepare_dataset_molecule(config)

    assert checksum
    assert [nucleus.label for nucleus in molecule.nuclei] == ["H1", "H2"]
    assert all(nucleus.A.tensor_full is not None for nucleus in molecule.nuclei)
    assert all(0.0 <= nucleus.shift.dia <= 10.0 for nucleus in molecule.nuclei)
