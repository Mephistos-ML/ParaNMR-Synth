import pytest

from paranmr_synth.cfg.dataset import DatasetGenerationConfig


def _config(number_of_moments: int = 10) -> dict:
    return {
        "project": {"name": "ybl8", "n_cases": 100, "seed": 42},
        "hyperfine": {
            "method": "pdip",
            "file": "YbL8.xyz",
            "paramagnetic_centre": [0.0, 0.0, 0.0],
            "spin": 0.5,
            "orbit": 3,
            "total_momentum_J": 3.5,
        },
        "nuclei": {"include": "H"},
        "diamagnetic": {"method": "csv", "file": "dia.csv"},
        "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7},
        "moments": {"number_of_moments": number_of_moments},
        "linewidth": {"method": "r6", "variables": {"p1": [500.0, 2000.0], "p2": [0.0, 1.0]}},
        "susceptibility": {"model": "isoaxrho_euler", "variables": {"iso": [0.0, 0.02], "ax": [-0.08, 0.08], "rho_over_ax": [0.0, 0.3333333333], "alpha": [0.0, 360.0], "beta": [0.0, 180.0], "gamma": [0.0, 360.0]}},
    }


def test_dataset_config_builds_dynamic_moment_labels():
    config = DatasetGenerationConfig.from_mapping(_config(number_of_moments=10))

    assert config.moment_labels == tuple(f"m{index}" for index in range(1, 11))
    assert config.linewidth.method == "r6"
    assert config.susceptibility.model == "isoaxrho_euler"


def test_dataset_config_requires_number_of_moments():
    raw = _config()
    del raw["moments"]["number_of_moments"]

    with pytest.raises(KeyError):
        DatasetGenerationConfig.from_mapping(raw)


def test_dataset_config_requires_dft_reference_input():
    raw = _config()
    raw["diamagnetic"] = {"method": "dft", "file": "dia.out"}

    with pytest.raises(ValueError, match="requires"):
        DatasetGenerationConfig.from_mapping(raw)
