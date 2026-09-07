"""Tensor-series generation orchestration."""

from __future__ import annotations

import numpy as np

from paranmr_synth.core.domain import IsoAxRhoLatents, TensorPoint, TensorSeries
from paranmr_synth.core.generators.priors import ParameterSpec, SeriesGeneratorSpec
from paranmr_synth.core.generators.temperature_dependence import (
    apply_curie_like_temperature_dependence,
)
from paranmr_synth.core.parameterizations import build_tensor_from_isoaxrho


def _sample_parameter(spec: ParameterSpec, rng: np.random.Generator) -> float:
    if spec.is_fixed:
        return spec.lower
    return float(rng.uniform(spec.lower, spec.upper))


def generate_tensor_series(
    spec: SeriesGeneratorSpec,
    rng: np.random.Generator,
) -> TensorSeries:
    """Generate one temperature-dependent susceptibility tensor series."""

    reference_latents = IsoAxRhoLatents(
        chi_iso=_sample_parameter(spec.chi_iso, rng),
        chi_ax=_sample_parameter(spec.chi_ax, rng),
        rho_over_ax=_sample_parameter(spec.rho_over_ax, rng),
        alpha_deg=_sample_parameter(spec.orientation.alpha_deg, rng),
        beta_deg=_sample_parameter(spec.orientation.beta_deg, rng),
        gamma_deg=_sample_parameter(spec.orientation.gamma_deg, rng),
    )

    temperatures_k = spec.temperature_grid.temperatures_k
    series_latents = apply_curie_like_temperature_dependence(
        reference_latents=reference_latents,
        temperatures_k=temperatures_k,
    )

    points = tuple(
        TensorPoint(
            tensor=build_tensor_from_isoaxrho(latents),
            temperature_k=temperature_k,
            latents=latents,
        )
        for temperature_k, latents in zip(temperatures_k, series_latents)
    )
    return TensorSeries(
        points=points,
        metadata={
            "sampled_chi_iso": _format_metadata_value(reference_latents.chi_iso),
            "sampled_chi_ax": _format_metadata_value(reference_latents.chi_ax),
            "sampled_rho_over_ax": _format_metadata_value(reference_latents.rho_over_ax),
            "sampled_alpha_deg": _format_metadata_value(reference_latents.alpha_deg),
            "sampled_beta_deg": _format_metadata_value(reference_latents.beta_deg),
            "sampled_gamma_deg": _format_metadata_value(reference_latents.gamma_deg),
        },
    )


def generate_tensor_series_batch(
    spec: SeriesGeneratorSpec,
    rng: np.random.Generator,
) -> tuple[TensorSeries, ...]:
    """Generate a batch of susceptibility tensor series."""

    return tuple(generate_tensor_series(spec, rng) for _ in range(spec.n_series))


def _format_metadata_value(value: float) -> str:
    return f"{float(value):.6f}"
