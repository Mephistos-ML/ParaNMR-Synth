"""Generator-layer public exports."""

from paranmr_synth.core.generators.priors import (
    OrientationSpec,
    ParameterSpec,
    SeriesGeneratorSpec,
    TemperatureGridSpec,
)
from paranmr_synth.core.generators.tensor_series import (
    generate_tensor_series,
    generate_tensor_series_batch,
)
from paranmr_synth.core.generators.temperature_dependence import (
    apply_curie_like_temperature_dependence,
)
from paranmr_synth.core.generators.diamagnetic import generate_diamagnetic_shifts
from paranmr_synth.core.generators.linewidth import (
    LinewidthLatents,
    generate_linewidth_latents,
)
from paranmr_synth.core.generators.susceptibility import (
    SusceptibilityLatents,
    generate_susceptibility_latents,
)

__all__ = [
    "apply_curie_like_temperature_dependence",
    "generate_tensor_series",
    "generate_tensor_series_batch",
    "generate_diamagnetic_shifts",
    "generate_linewidth_latents",
    "generate_susceptibility_latents",
    "LinewidthLatents",
    "OrientationSpec",
    "ParameterSpec",
    "SeriesGeneratorSpec",
    "TemperatureGridSpec",
    "SusceptibilityLatents",
]
