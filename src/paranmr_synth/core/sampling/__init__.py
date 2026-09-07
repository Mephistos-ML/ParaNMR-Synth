"""Deterministic samplers for synthetic-experiment nuisance variables."""

from paranmr_synth.core.sampling.diamagnetic import sample_diamagnetic_shifts
from paranmr_synth.core.sampling.latents import SampledLatents, sample_latents

__all__ = ["SampledLatents", "sample_diamagnetic_shifts", "sample_latents"]
