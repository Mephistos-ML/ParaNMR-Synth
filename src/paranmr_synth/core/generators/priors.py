"""Generator-side parameter specifications."""

from __future__ import annotations

from dataclasses import dataclass

from paranmr_synth.core.constraints import (
    validate_n_series,
    validate_parameter_bounds,
    validate_temperature_grid,
)


@dataclass(frozen=True, slots=True)
class ParameterSpec:
    """Sampling specification for one scalar generator parameter."""

    lower: float
    upper: float

    def __post_init__(self) -> None:
        lower, upper = validate_parameter_bounds(self.lower, self.upper)
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)

    @classmethod
    def from_raw(cls, value: float | int | list[float] | tuple[float, float]) -> "ParameterSpec":
        """Build a parameter specification from scalar or two-element bounds."""

        if isinstance(value, (int, float)):
            scalar = float(value)
            return cls(lower=scalar, upper=scalar)

        if isinstance(value, (list, tuple)) and len(value) == 2:
            return cls(lower=float(value[0]), upper=float(value[1]))

        raise ValueError(
            "ParameterSpec expects either a scalar fixed value or a two-element bounds list."
        )

    @property
    def is_fixed(self) -> bool:
        """Return whether the parameter is fixed to one value."""

        return self.lower == self.upper


@dataclass(frozen=True, slots=True)
class TemperatureGridSpec:
    """Integer temperature grid specification for one tensor series."""

    start: int
    stop: int
    step: int = 1

    def __post_init__(self) -> None:
        start, stop, step = validate_temperature_grid(self.start, self.stop, self.step)
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "stop", stop)
        object.__setattr__(self, "step", step)

    @property
    def temperatures_k(self) -> tuple[int, ...]:
        """Return the integer temperature grid implied by the specification."""

        return tuple(range(self.start, self.stop + 1, self.step))


@dataclass(frozen=True, slots=True)
class OrientationSpec:
    """Sampling specification for one shared series orientation."""

    alpha_deg: ParameterSpec
    beta_deg: ParameterSpec
    gamma_deg: ParameterSpec


@dataclass(frozen=True, slots=True)
class SeriesGeneratorSpec:
    """Typed generator specification for a batch of tensor series."""

    n_series: int
    temperature_grid: TemperatureGridSpec
    chi_iso: ParameterSpec
    chi_ax: ParameterSpec
    rho_over_ax: ParameterSpec
    orientation: OrientationSpec

    def __post_init__(self) -> None:
        n_series = validate_n_series(self.n_series)
        object.__setattr__(self, "n_series", n_series)
