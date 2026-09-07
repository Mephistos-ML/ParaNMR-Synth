"""Typed configuration section models."""

from __future__ import annotations

from dataclasses import dataclass

from paranmr_synth.core.generators.specs import ParameterSpec


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    name: str
    n_cases: int
    seed: int


@dataclass(frozen=True, slots=True)
class HyperfineConfig:
    file: str
    paramagnetic_centre: tuple[float, float, float]
    spin: float
    orbit: float
    total_momentum_j: float


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    temperature_k: float
    magnetic_field_t: float


@dataclass(frozen=True, slots=True)
class DiamagneticConfig:
    range_min_ppm: float
    range_max_ppm: float


@dataclass(frozen=True, slots=True)
class LinewidthConfig:
    method: str
    p1: ParameterSpec
    p2: ParameterSpec


@dataclass(frozen=True, slots=True)
class SusceptibilityConfig:
    model: str
    input_units: str
    iso: ParameterSpec
    ax: ParameterSpec
    rho_over_ax: ParameterSpec
    alpha: ParameterSpec
    beta: ParameterSpec
    gamma: ParameterSpec
