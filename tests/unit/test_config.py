from paranmr_synth.cfg import GenerateConfig


def test_generate_config_from_file_builds_series_generator_spec(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "\n".join(
            [
                "generator:",
                "  n_series: 2",
                "  seed: 7",
                "temperature:",
                "  start: 280",
                "  stop: 282",
                "  step: 1",
                "chi_iso: 10.0",
                "chi_ax: [0.0, 3.0]",
                "rho_over_ax: [0.0, 0.3333333333]",
                "orientation:",
                "  alpha_deg: 0.0",
                "  beta_deg: [0.0, 180.0]",
                "  gamma_deg: [0.0, 360.0]",
                "output_name: generated_series",
            ]
        ),
        encoding="utf-8",
    )

    config = GenerateConfig.from_file(config_file)
    spec = config.to_series_generator_spec()

    assert config.seed == 7
    assert config.output_name == "generated_series"
    assert spec.n_series == 2
    assert spec.temperature_grid.temperatures_k == (280, 281, 282)
    assert spec.chi_iso.is_fixed is True
    assert spec.chi_ax.lower == 0.0
    assert spec.chi_ax.upper == 3.0
