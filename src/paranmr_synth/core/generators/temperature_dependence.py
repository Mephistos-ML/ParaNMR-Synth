"""Temperature-dependent evolution helpers for tensor-series generation."""

from __future__ import annotations

from paranmr_synth.core.domain import IsoAxRhoLatents


def apply_curie_like_temperature_dependence(
    reference_latents: IsoAxRhoLatents,
    temperatures_k: tuple[int, ...] | list[int],
) -> tuple[IsoAxRhoLatents, ...]:
    """Expand one reference latent state into a temperature-dependent series.

    The reference susceptibility values are interpreted at the maximum
    temperature in the series. For each temperature ``T``, the isotropic and
    axial components scale as ``T_ref / T`` while ``rho_over_ax`` and Euler
    angles remain constant across the series.
    """

    temperatures = tuple(int(temperature) for temperature in temperatures_k)
    if not temperatures:
        raise ValueError("Temperature-dependent expansion requires at least one temperature.")

    t_ref = max(temperatures)
    series_latents: list[IsoAxRhoLatents] = []
    for temperature in temperatures:
        scale = float(t_ref) / float(temperature)
        series_latents.append(
            IsoAxRhoLatents(
                chi_iso=reference_latents.chi_iso * scale,
                chi_ax=reference_latents.chi_ax * scale,
                rho_over_ax=reference_latents.rho_over_ax,
                alpha_deg=reference_latents.alpha_deg,
                beta_deg=reference_latents.beta_deg,
                gamma_deg=reference_latents.gamma_deg,
            )
        )

    return tuple(series_latents)
