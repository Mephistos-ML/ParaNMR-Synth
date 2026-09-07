"""YAML-backed configuration for tensor-series generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from paranmr_synth.core.generators import (
    OrientationSpec,
    ParameterSpec,
    SeriesGeneratorSpec,
    TemperatureGridSpec,
)


@dataclass(frozen=True, slots=True)
class GenerateConfig:
    """YAML-facing configuration object for `paranmr-synth run`."""

    n_series: int
    temperature_start: int
    temperature_stop: int
    temperature_step: int
    chi_iso: float | int | list[float] | tuple[float, float]
    chi_ax: float | int | list[float] | tuple[float, float]
    rho_over_ax: float | int | list[float] | tuple[float, float]
    alpha_deg: float | int | list[float] | tuple[float, float] = 0.0
    beta_deg: float | int | list[float] | tuple[float, float] = 0.0
    gamma_deg: float | int | list[float] | tuple[float, float] = 0.0
    output_name: str | None = None
    seed: int | None = None

    @classmethod
    def from_file(cls, file_name: str | Path) -> "GenerateConfig":
        """Load a generation config from a YAML file."""

        path = Path(file_name)
        with path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)

        if not isinstance(raw, dict):
            raise ValueError("Generation config root must be a YAML mapping.")

        return cls.from_mapping(raw)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "GenerateConfig":
        """Build a generation config from a parsed YAML mapping."""

        generator = _require_mapping(raw, "generator")
        temperature = _require_mapping(raw, "temperature")
        orientation = raw.get("orientation", {})

        if not isinstance(orientation, dict):
            raise ValueError("orientation must be a mapping when provided.")

        return cls(
            n_series=int(generator["n_series"]),
            seed=_optional_int(generator.get("seed")),
            temperature_start=int(temperature["start"]),
            temperature_stop=int(temperature["stop"]),
            temperature_step=int(temperature.get("step", 1)),
            chi_iso=raw["chi_iso"],
            chi_ax=raw["chi_ax"],
            rho_over_ax=raw["rho_over_ax"],
            alpha_deg=orientation.get("alpha_deg", 0.0),
            beta_deg=orientation.get("beta_deg", 0.0),
            gamma_deg=orientation.get("gamma_deg", 0.0),
            output_name=_optional_str(raw.get("output_name")),
        )

    def to_series_generator_spec(self) -> SeriesGeneratorSpec:
        """Convert the YAML-facing config into the canonical generator spec."""

        return SeriesGeneratorSpec(
            n_series=self.n_series,
            temperature_grid=TemperatureGridSpec(
                start=self.temperature_start,
                stop=self.temperature_stop,
                step=self.temperature_step,
            ),
            chi_iso=ParameterSpec.from_raw(self.chi_iso),
            chi_ax=ParameterSpec.from_raw(self.chi_ax),
            rho_over_ax=ParameterSpec.from_raw(self.rho_over_ax),
            orientation=OrientationSpec(
                alpha_deg=ParameterSpec.from_raw(self.alpha_deg),
                beta_deg=ParameterSpec.from_raw(self.beta_deg),
                gamma_deg=ParameterSpec.from_raw(self.gamma_deg),
            ),
        )

    def to_report_metadata(self) -> dict[str, str]:
        """Return YAML-facing generation settings for CSV provenance comments."""

        metadata: dict[str, str] = {
            "seed": "None" if self.seed is None else str(self.seed),
            "chi_iso": _format_yaml_value(self.chi_iso),
            "chi_ax": _format_yaml_value(self.chi_ax),
            "rho_over_ax": _format_yaml_value(self.rho_over_ax),
            "alpha_deg": _format_yaml_value(self.alpha_deg),
            "beta_deg": _format_yaml_value(self.beta_deg),
            "gamma_deg": _format_yaml_value(self.gamma_deg),
        }
        return metadata


def _require_mapping(raw: dict[str, Any], key: str) -> dict[str, Any]:
    value = raw.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a YAML mapping.")
    return value


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return text


def _format_yaml_value(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_format_yaml_value(item) for item in value) + "]"
    return str(value)
