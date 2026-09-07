import numpy as np
import pytest

from paranmr_synth.core.generators import (
    OrientationSpec,
    ParameterSpec,
    SeriesGeneratorSpec,
    TemperatureGridSpec,
    apply_curie_like_temperature_dependence,
    generate_tensor_series,
    generate_tensor_series_batch,
)
from paranmr_synth.core.domain import IsoAxRhoLatents


def test_parameter_spec_from_scalar_creates_fixed_spec():
    spec = ParameterSpec.from_raw(0.1)

    assert spec.lower == 0.1
    assert spec.upper == 0.1
    assert spec.is_fixed is True


def test_parameter_spec_from_bounds_creates_uniform_spec():
    spec = ParameterSpec.from_raw([0.0, 1.0])

    assert spec.lower == 0.0
    assert spec.upper == 1.0
    assert spec.is_fixed is False


def test_temperature_grid_spec_returns_integer_grid():
    spec = TemperatureGridSpec(start=280, stop=285, step=2)

    assert spec.temperatures_k == (280, 282, 284)


def test_series_generator_spec_accepts_shared_orientation_spec():
    spec = SeriesGeneratorSpec(
        n_series=10,
        temperature_grid=TemperatureGridSpec(start=280, stop=285, step=1),
        chi_iso=ParameterSpec.from_raw([0.0, 10.0]),
        chi_ax=ParameterSpec.from_raw([-5.0, 5.0]),
        rho_over_ax=ParameterSpec.from_raw([0.0, 1.0 / 3.0]),
        orientation=OrientationSpec(
            alpha_deg=ParameterSpec.from_raw([0.0, 360.0]),
            beta_deg=ParameterSpec.from_raw([0.0, 180.0]),
            gamma_deg=ParameterSpec.from_raw([0.0, 360.0]),
        ),
    )

    assert spec.n_series == 10
    assert spec.temperature_grid.temperatures_k == (280, 281, 282, 283, 284, 285)


def test_apply_curie_like_temperature_dependence_scales_to_max_temperature():
    reference = IsoAxRhoLatents(
        chi_iso=10.0,
        chi_ax=3.0,
        rho_over_ax=1.0 / 6.0,
        alpha_deg=30.0,
        beta_deg=45.0,
        gamma_deg=60.0,
    )

    latents_series = apply_curie_like_temperature_dependence(
        reference,
        temperatures_k=(280, 285),
    )

    assert len(latents_series) == 2
    assert latents_series[1].chi_iso == 10.0
    assert latents_series[1].chi_ax == 3.0
    assert latents_series[0].chi_iso == pytest.approx(10.0 * 285.0 / 280.0)
    assert latents_series[0].chi_ax == pytest.approx(3.0 * 285.0 / 280.0)
    assert latents_series[0].rho_over_ax == reference.rho_over_ax
    assert latents_series[0].alpha_deg == reference.alpha_deg


def test_generate_tensor_series_builds_ordered_series_with_shared_orientation():
    spec = SeriesGeneratorSpec(
        n_series=2,
        temperature_grid=TemperatureGridSpec(start=280, stop=282, step=1),
        chi_iso=ParameterSpec.from_raw(10.0),
        chi_ax=ParameterSpec.from_raw(3.0),
        rho_over_ax=ParameterSpec.from_raw(1.0 / 6.0),
        orientation=OrientationSpec(
            alpha_deg=ParameterSpec.from_raw(30.0),
            beta_deg=ParameterSpec.from_raw(45.0),
            gamma_deg=ParameterSpec.from_raw(60.0),
        ),
    )

    series = generate_tensor_series(spec, np.random.default_rng(7))

    assert series.temperatures_k == (280.0, 281.0, 282.0)
    assert len(series.points) == 3
    assert all(point.latents.alpha_deg == 30.0 for point in series.points)
    assert all(point.latents.beta_deg == 45.0 for point in series.points)
    assert all(point.latents.gamma_deg == 60.0 for point in series.points)
    assert series.points[-1].latents.chi_iso == 10.0
    assert series.metadata["sampled_chi_iso"] == "10.000000"
    assert series.metadata["sampled_chi_ax"] == "3.000000"
    assert series.metadata["sampled_rho_over_ax"] == "0.166667"


def test_generate_tensor_series_batch_uses_n_series():
    spec = SeriesGeneratorSpec(
        n_series=3,
        temperature_grid=TemperatureGridSpec(start=280, stop=280, step=1),
        chi_iso=ParameterSpec.from_raw(10.0),
        chi_ax=ParameterSpec.from_raw(3.0),
        rho_over_ax=ParameterSpec.from_raw(1.0 / 6.0),
        orientation=OrientationSpec(
            alpha_deg=ParameterSpec.from_raw(0.0),
            beta_deg=ParameterSpec.from_raw(0.0),
            gamma_deg=ParameterSpec.from_raw(0.0),
        ),
    )

    batch = generate_tensor_series_batch(spec, np.random.default_rng(11))

    assert len(batch) == 3
    assert all(series.temperatures_k == (280.0,) for series in batch)
