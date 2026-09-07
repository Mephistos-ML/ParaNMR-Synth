import pytest

from paranmr_synth.cfg import DatasetGenerationConfig


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
        "diamagnetic": {"range_min_ppm": 0.0, "range_max_ppm": 10.0},
        "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7},
        "moments": {"number_of_moments": number_of_moments},
        "linewidth": {"method": "r6"},
        "susceptibility": {"model": "isoaxrho_euler"},
    }


def test_dataset_config_builds_dynamic_moment_labels():
    config = DatasetGenerationConfig.from_mapping(_config(number_of_moments=10))

    assert config.moment_labels == tuple(f"m{index}" for index in range(1, 11))
    assert config.linewidth_method == "r6"
    assert config.susceptibility_model == "isoaxrho_euler"


def test_dataset_config_requires_number_of_moments():
    raw = _config()
    del raw["moments"]["number_of_moments"]

    with pytest.raises(KeyError):
        DatasetGenerationConfig.from_mapping(raw)


def test_dataset_config_rejects_invalid_diamagnetic_range():
    raw = _config()
    raw["diamagnetic"] = {"range_min_ppm": 10.0, "range_max_ppm": 0.0}

    with pytest.raises(ValueError, match="must not exceed"):
        DatasetGenerationConfig.from_mapping(raw)
