from paranmr_synth.cfg.dataset import DatasetGenerationConfig
from paranmr_synth.core.generators.linewidth import generate_linewidth_latents
from paranmr_synth.core.generators.susceptibility import generate_susceptibility_latents
from paranmr.core.phys.susc import get_spin_only_susc


def test_latent_sampling_is_stable_per_case_and_parameter():
    raw = {
        "project": {"name": "test", "n_cases": 2, "seed": 42},
        "hyperfine": {"method": "pdip", "file": "test.xyz", "paramagnetic_centre": [0, 0, 0], "spin": 0.5, "orbit": 3, "total_momentum_J": 3.5},
        "nuclei": {"include": "H"},
        "diamagnetic": {"method": "csv", "file": "dia.csv"},
        "experiment": {"temperature_k": 302.15, "magnetic_field_t": 4.7},
        "moments": {"number_of_moments": 10},
        "linewidth": {"method": "r6", "variables": {"p1": [500, 2000], "p2": [0, 1]}},
        "susceptibility": {"model": "isoaxrho_euler"},
    }
    config = DatasetGenerationConfig.from_mapping(raw)
    first = generate_susceptibility_latents(config=config, geometry_checksum="abc", case_index=0)
    repeated = generate_susceptibility_latents(config=config, geometry_checksum="abc", case_index=0)
    second = generate_susceptibility_latents(config=config, geometry_checksum="abc", case_index=1)
    linewidth = generate_linewidth_latents(config=config, geometry_checksum="abc", case_index=0)

    assert first == repeated
    assert first != second
    assert first.iso == get_spin_only_susc(
        spin=config.hyperfine.spin,
        orbit=config.hyperfine.orbit,
        total_momentum_J=config.hyperfine.total_momentum_j,
        temperature=config.experiment.temperature_k,
    )
    principal_components = (
        first.iso + first.ax * (first.rho_over_ax - 1.0 / 3.0),
        first.iso - first.ax * (first.rho_over_ax + 1.0 / 3.0),
        first.iso + 2.0 * first.ax / 3.0,
    )
    assert min(principal_components) >= 0.0
    assert 0.0 <= first.rho_over_ax <= 1.0 / 3.0
    assert 500.0 <= linewidth.p1 <= 2000.0
