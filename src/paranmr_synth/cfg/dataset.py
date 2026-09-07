"""Strict YAML contract for synthetic moment-dataset generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from paranmr.app.policies.susc import normalize_susc_fit_input_units

from paranmr_synth.cfg.models import (
    DiamagneticConfig, ExperimentConfig, HyperfineConfig, LinewidthConfig,
    ProjectConfig, SusceptibilityConfig,
)
from paranmr_synth.core.generators.specs import ParameterSpec


@dataclass(frozen=True, slots=True)
class DatasetGenerationConfig:
    """Validated public configuration for one synthetic dataset run."""

    project: ProjectConfig
    hyperfine: HyperfineConfig
    nuclei_include: str
    diamagnetic: DiamagneticConfig
    experiment: ExperimentConfig
    number_of_moments: int
    linewidth: LinewidthConfig
    susceptibility: SusceptibilityConfig

    @classmethod
    def from_file(cls, file_name: str | Path) -> "DatasetGenerationConfig":
        """Load and validate one dataset-generation YAML file."""
        path = Path(file_name).resolve()
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle)
        if not isinstance(raw, dict):
            raise ValueError("Dataset configuration root must be a mapping")
        hyperfine = _mapping(raw, "hyperfine")
        hyperfine_file = Path(str(hyperfine["file"]))
        if not hyperfine_file.is_absolute():
            hyperfine["file"] = str(path.parent / hyperfine_file)
        return cls.from_mapping(raw)

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "DatasetGenerationConfig":
        """Build the typed contract from parsed YAML content."""
        project = _mapping(raw, "project")
        hyperfine = _mapping(raw, "hyperfine")
        nuclei = _mapping(raw, "nuclei")
        diamagnetic = _mapping(raw, "diamagnetic")
        experiment = _mapping(raw, "experiment")
        moments = _mapping(raw, "moments")
        linewidth = _mapping(raw, "linewidth")
        susceptibility = _mapping(raw, "susceptibility")
        method = str(hyperfine["method"]).lower()
        if method != "pdip":
            raise ValueError("hyperfine.method must be 'pdip'")
        linewidth_method = str(linewidth["method"]).lower()
        if linewidth_method != "r6":
            raise ValueError("linewidth.method must be 'r6'")
        model = str(susceptibility["model"]).lower()
        if model != "isoaxrho_euler":
            raise ValueError("susceptibility.model must be 'isoaxrho_euler'")
        input_units = normalize_susc_fit_input_units(susceptibility.get("input_units"))
        linewidth_variables = _mapping(linewidth, "variables")
        susceptibility_variables = _mapping(susceptibility, "variables")
        rho_over_ax = ParameterSpec.from_raw(susceptibility_variables["rho_over_ax"])
        if rho_over_ax.lower < 0.0 or rho_over_ax.upper > 1.0 / 3.0:
            raise ValueError("rho_over_ax bounds must lie within [0, 1/3]")
        centre = tuple(float(value) for value in hyperfine["paramagnetic_centre"])
        if len(centre) != 3:
            raise ValueError("hyperfine.paramagnetic_centre must have three values")
        minimum = float(diamagnetic["range_min_ppm"])
        maximum = float(diamagnetic["range_max_ppm"])
        if minimum > maximum:
            raise ValueError("diamagnetic range_min_ppm must not exceed range_max_ppm")
        n_cases = int(project["n_cases"])
        number_of_moments = int(moments["number_of_moments"])
        if n_cases <= 0 or number_of_moments <= 0:
            raise ValueError("n_cases and number_of_moments must be positive")
        return cls(
            project=ProjectConfig(_nonempty(project["name"], "project.name"), n_cases, int(project["seed"])),
            hyperfine=HyperfineConfig(_nonempty(hyperfine["file"], "hyperfine.file"), centre, float(hyperfine["spin"]), float(hyperfine["orbit"]), float(hyperfine["total_momentum_J"])),
            nuclei_include=_nonempty(nuclei["include"], "nuclei.include"),
            diamagnetic=DiamagneticConfig(minimum, maximum),
            experiment=ExperimentConfig(float(experiment["temperature_k"]), float(experiment["magnetic_field_t"])),
            number_of_moments=number_of_moments,
            linewidth=LinewidthConfig(linewidth_method, ParameterSpec.from_raw(linewidth_variables["p1"]), ParameterSpec.from_raw(linewidth_variables["p2"])),
            susceptibility=SusceptibilityConfig(model, input_units, ParameterSpec.from_raw(susceptibility_variables["iso"]), ParameterSpec.from_raw(susceptibility_variables["ax"]), rho_over_ax, ParameterSpec.from_raw(susceptibility_variables["alpha"]), ParameterSpec.from_raw(susceptibility_variables["beta"]), ParameterSpec.from_raw(susceptibility_variables["gamma"])),
        )

    @property
    def moment_labels(self) -> tuple[str, ...]:
        """Return dynamic canonical labels from ``m1`` through ``mN``."""
        return tuple(f"m{index}" for index in range(1, self.number_of_moments + 1))


def _mapping(raw: dict[str, Any], name: str) -> dict[str, Any]:
    value = raw.get(name)
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def _nonempty(value: object, name: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text
