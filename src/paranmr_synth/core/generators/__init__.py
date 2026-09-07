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

__all__ = [
    "apply_curie_like_temperature_dependence",
    "generate_tensor_series",
    "generate_tensor_series_batch",
    "OrientationSpec",
    "ParameterSpec",
    "SeriesGeneratorSpec",
    "TemperatureGridSpec",
]
