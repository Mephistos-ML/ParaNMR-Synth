import csv
import sys

from paranmr_synth.app.pipelines import run_generate
from paranmr_synth.cli.main import main
from paranmr_synth.core.domain import IsoAxRhoLatents, TensorPoint, TensorSeries
from paranmr_synth.core.generators import (
    OrientationSpec,
    ParameterSpec,
    SeriesGeneratorSpec,
    TemperatureGridSpec,
)
from paranmr_synth.io import write_paranmr_csv
from paranmr_synth.core.parameterizations import build_tensor_from_isoaxrho


def test_write_paranmr_csv_exports_expected_columns(tmp_path):
    latents = IsoAxRhoLatents(
        chi_iso=10.0,
        chi_ax=3.0,
        rho_over_ax=1.0 / 6.0,
        alpha_deg=30.0,
        beta_deg=45.0,
        gamma_deg=60.0,
    )
    point = TensorPoint(
        tensor=build_tensor_from_isoaxrho(latents),
        temperature_k=298.15,
        latents=latents,
    )
    series = TensorSeries(
        points=(point,),
        metadata={
            "chi_iso": "10.000000",
            "chi_ax": "3.000000",
            "rho_over_ax": "0.166667",
            "alpha_deg": "30.000000",
            "beta_deg": "45.000000",
            "gamma_deg": "60.000000",
        },
    )

    out_file = tmp_path / "susceptibility.csv"
    write_paranmr_csv(series, out_file)

    with out_file.open("r", newline="", encoding="utf-8-sig") as handle:
        lines = [line for line in handle if not line.startswith("#")]
        reader = csv.DictReader(lines)
        rows = list(reader)

    raw_text = out_file.read_text(encoding="utf-8-sig")
    comment_lines = [line for line in raw_text.splitlines() if line.startswith("#")]

    assert len(rows) == 1
    assert comment_lines[0].startswith("# This file was generated with paraNMR-Synth v")
    assert comment_lines[1] == "# paranmr/simpnmr-compatible susceptibility tensor series"
    assert (
        comment_lines[2]
        == "# seed=None, chi_iso=10.000000, chi_ax=3.000000, rho_over_ax=0.166667, "
        "alpha_deg=30.000000, beta_deg=45.000000, gamma_deg=60.000000"
    )
    assert reader.fieldnames == [
        "Temperature (K)",
        "chi_iso (Å^3)",
        "chi_ax (Å^3)",
        "chi_rho (Å^3)",
        "chi_xx (Å^3)",
        "chi_xy (Å^3)",
        "chi_xz (Å^3)",
        "chi_yy (Å^3)",
        "chi_yz (Å^3)",
        "chi_zz (Å^3)",
        "dchi_xx (Å^3)",
        "dchi_xy (Å^3)",
        "dchi_xz (Å^3)",
        "dchi_yy (Å^3)",
        "dchi_yz (Å^3)",
        "dchi_zz (Å^3)",
        "chi_x (Å^3)",
        "chi_y (Å^3)",
        "chi_z (Å^3)",
        "alpha (degrees)",
        "beta (degrees)",
        "gamma (degrees)",
    ]
    assert rows[0]["Temperature (K)"] == "298.15"
    assert rows[0]["chi_iso (Å^3)"] == "10.000000"
    assert rows[0]["chi_ax (Å^3)"] == "3.000000"
    assert rows[0]["chi_rho (Å^3)"] == "0.500000"


def test_run_generate_runs_end_to_end(tmp_path):
    spec = SeriesGeneratorSpec(
        n_series=2,
        temperature_grid=TemperatureGridSpec(start=280, stop=281, step=1),
        chi_iso=ParameterSpec.from_raw(10.0),
        chi_ax=ParameterSpec.from_raw(3.0),
        rho_over_ax=ParameterSpec.from_raw(1.0 / 6.0),
        orientation=OrientationSpec(
            alpha_deg=ParameterSpec.from_raw(0.0),
            beta_deg=ParameterSpec.from_raw(0.0),
            gamma_deg=ParameterSpec.from_raw(0.0),
        ),
    )

    written_files = run_generate(
        spec,
        output_dir=tmp_path,
        seed=7,
        series_metadata={
            "seed": "7",
            "chi_iso": "10.0",
            "chi_ax": "3.0",
            "rho_over_ax": "0.16666666666666666",
            "alpha_deg": "0.0",
            "beta_deg": "0.0",
            "gamma_deg": "0.0",
        },
    )

    assert len(written_files) == 2
    assert written_files[0].name == "susceptibility_tensor_1_280K_to_281K.csv"
    assert written_files[1].name == "susceptibility_tensor_2_280K_to_281K.csv"
    assert all(path.exists() for path in written_files)
    first_text = written_files[0].read_text(encoding="utf-8-sig")
    assert "# seed=7, chi_iso=10.0, chi_ax=3.0, rho_over_ax=0.16666666666666666, alpha_deg=0.0, beta_deg=0.0, gamma_deg=0.0" in first_text


def test_cli_run_executes_generation_from_yaml_config(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "\n".join(
            [
                "generator:",
                "  n_series: 1",
                "  seed: 7",
                "temperature:",
                "  start: 280",
                "  stop: 281",
                "  step: 1",
                "chi_iso: [9.0, 10.0]",
                "chi_ax: [-4.0, 3.0]",
                "rho_over_ax: [0.0, 0.1666666667]",
                "orientation:",
                "  alpha_deg: [0.0, 30.0]",
                "  beta_deg: 0.0",
                "  gamma_deg: [0.0, 60.0]",
                "output_name: my_series",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(sys, "argv", ["paranmr-synth", "run", str(config_file)])

    exit_code = main()

    assert exit_code == 0
    out_file = tmp_path / "my_series" / "susceptibility_tensor_1_280K_to_281K.csv"
    assert out_file.exists()
    out_text = out_file.read_text(encoding="utf-8-sig")
    assert "# seed=7, chi_iso=[9.0, 10.0], chi_ax=[-4.0, 3.0], rho_over_ax=[0.0, 0.1666666667], alpha_deg=[0.0, 30.0], beta_deg=0.0, gamma_deg=[0.0, 60.0]" in out_text
