"""Sampling-spec validation rules."""

from __future__ import annotations


def validate_parameter_bounds(lower: float, upper: float) -> tuple[float, float]:
    """Validate fixed or bounded scalar sampling parameters."""

    lower_value = float(lower)
    upper_value = float(upper)
    if lower_value > upper_value:
        raise ValueError("ParameterSpec requires lower <= upper for fixed values or bounds.")
    return lower_value, upper_value


def validate_temperature_grid(start: int, stop: int, step: int) -> tuple[int, int, int]:
    """Validate an integer temperature grid."""

    start_value = int(start)
    stop_value = int(stop)
    step_value = int(step)

    if step_value <= 0:
        raise ValueError("TemperatureGridSpec.step must be a positive integer.")
    if start_value > stop_value:
        raise ValueError("TemperatureGridSpec requires start <= stop.")

    return start_value, stop_value, step_value


def validate_n_series(n_series: int) -> int:
    """Validate the number of generated series."""

    value = int(n_series)
    if value <= 0:
        raise ValueError("SeriesGeneratorSpec.n_series must be a positive integer.")
    return value
