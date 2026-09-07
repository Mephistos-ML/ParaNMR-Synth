"""Series-oriented domain objects for generated susceptibility tensors."""

from __future__ import annotations

from dataclasses import dataclass, field

from paranmr_synth.core.constraints import (
    validate_euler_zyz_angles_deg,
    validate_positive_temperature_k,
    validate_rho_over_ax,
    validate_strictly_increasing_temperatures,
)
from paranmr_synth.core.domain.tensors import SusceptibilityTensor


@dataclass(frozen=True, slots=True)
class IsoAxRhoLatents:
    """ML-style latent representation used to generate a susceptibility tensor."""

    chi_iso: float
    chi_ax: float
    rho_over_ax: float
    alpha_deg: float = 0.0
    beta_deg: float = 0.0
    gamma_deg: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "chi_iso", float(self.chi_iso))
        object.__setattr__(self, "chi_ax", float(self.chi_ax))
        rho_over_ax = validate_rho_over_ax(self.rho_over_ax)
        object.__setattr__(self, "rho_over_ax", rho_over_ax)
        alpha_deg, beta_deg, gamma_deg = validate_euler_zyz_angles_deg(
            self.alpha_deg,
            self.beta_deg,
            self.gamma_deg,
        )
        object.__setattr__(self, "alpha_deg", alpha_deg)
        object.__setattr__(self, "beta_deg", beta_deg)
        object.__setattr__(self, "gamma_deg", gamma_deg)


@dataclass(frozen=True, slots=True)
class TensorPoint:
    """One susceptibility tensor evaluated at one temperature."""

    tensor: SusceptibilityTensor
    temperature_k: float
    latents: IsoAxRhoLatents

    def __post_init__(self) -> None:
        temperature = validate_positive_temperature_k(self.temperature_k)
        object.__setattr__(self, "temperature_k", temperature)


@dataclass(frozen=True, slots=True)
class TensorSeries:
    """Ordered collection of susceptibility tensors across temperature."""

    points: tuple[TensorPoint, ...]
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        points = tuple(self.points)
        if not points:
            raise ValueError("TensorSeries must contain at least one TensorPoint.")

        validate_strictly_increasing_temperatures(point.temperature_k for point in points)
        object.__setattr__(self, "points", points)

    @property
    def temperatures_k(self) -> tuple[float, ...]:
        """Return the ordered temperature grid for the series."""

        return tuple(point.temperature_k for point in self.points)
