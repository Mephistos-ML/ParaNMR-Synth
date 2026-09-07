"""Canonical susceptibility-tensor domain objects."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from paranmr_synth.core.constraints import as_symmetric_tensor


@dataclass(frozen=True, slots=True)
class SusceptibilityTensor:
    """Magnetic susceptibility tensor in canonical internal units."""

    matrix_a3: NDArray[np.float64]

    def __post_init__(self) -> None:
        object.__setattr__(self, "matrix_a3", as_symmetric_tensor(self.matrix_a3))

    @property
    def chi_iso(self) -> float:
        """Return the isotropic susceptibility, ``trace(chi) / 3``."""

        return float(np.trace(self.matrix_a3) / 3.0)

    @property
    def delta_matrix_a3(self) -> NDArray[np.float64]:
        """Return the traceless anisotropic component of the tensor."""

        return self.matrix_a3 - np.eye(3) * self.chi_iso
