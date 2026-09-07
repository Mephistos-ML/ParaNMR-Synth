from paranmr_synth.cfg import DatasetGenerationConfig
from paranmr_synth.core.generators import (
    generate_linewidth_latents,
    generate_susceptibility_latents,
)


def test_latent_sampling_is_stable_per_case_and_parameter():
    raw = {
        "project": {"name": "test", "n_cases": 2, "seed": 42},
        "hyperfine": {"method": "pdip", "file": "test.xyz", "paramagnetic_centre": [0, 0, 0], "spin": 0.5, "orbit": 3, "total_momentum_J": 3.5},
        "nuclei": {"include": "H"},
        "diamagnetic": {"range_min_ppm": 0, "range_max_ppm": 10},
        "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7},
        "moments": {"number_of_moments": 10},
        "linewidth": {"method": "r6", "variables": {"p1": [500, 2000], "p2": [0, 1]}},
        "susceptibility": {"model": "isoaxrho_euler", "variables": {"iso": [0, 0.02], "ax": [-0.08, 0.08], "rho_over_ax": [0, 1 / 3], "alpha": [0, 360], "beta": [0, 180], "gamma": [0, 360]}},
    }
    config = DatasetGenerationConfig.from_mapping(raw)
    first = generate_susceptibility_latents(config=config, geometry_checksum="abc", case_index=0)
    repeated = generate_susceptibility_latents(config=config, geometry_checksum="abc", case_index=0)
    second = generate_susceptibility_latents(config=config, geometry_checksum="abc", case_index=1)
    linewidth = generate_linewidth_latents(config=config, geometry_checksum="abc", case_index=0)

    assert first == repeated
    assert first != second
    assert 0.0 <= first.rho_over_ax <= 1.0 / 3.0
    assert 500.0 <= linewidth.p1 <= 2000.0
