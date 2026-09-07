"""Adapters for paranmr-compatible file formats."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from paranmr_synth.core.domain import TensorSeries
from paranmr_synth.io.csv_utils import write_csv_rows_safe

logger = logging.getLogger(__name__)


def write_paranmr_csv(
    series: TensorSeries,
    file_name: str | Path,
) -> None:
    """Write a susceptibility series in the CSV layout expected by paranmr."""

    path = Path(file_name)
    rows: list[dict[str, float]] = []

    for point in series.points:
        tensor = point.tensor.matrix_a3
        delta = point.tensor.delta_matrix_a3
        eigvals = np.linalg.eigvalsh(tensor)
        eigvals = eigvals[np.argsort(np.abs(eigvals))]
        chi_rho = point.latents.rho_over_ax * point.latents.chi_ax

        rows.append(
            {
                "Temperature (K)": _format_temperature(point.temperature_k),
                "chi_iso (Å^3)": _format_tensor_value(point.tensor.chi_iso),
                "chi_ax (Å^3)": _format_tensor_value(point.latents.chi_ax),
                "chi_rho (Å^3)": _format_tensor_value(chi_rho),
                "chi_xx (Å^3)": _format_tensor_value(tensor[0, 0]),
                "chi_xy (Å^3)": _format_tensor_value(tensor[0, 1]),
                "chi_xz (Å^3)": _format_tensor_value(tensor[0, 2]),
                "chi_yy (Å^3)": _format_tensor_value(tensor[1, 1]),
                "chi_yz (Å^3)": _format_tensor_value(tensor[1, 2]),
                "chi_zz (Å^3)": _format_tensor_value(tensor[2, 2]),
                "dchi_xx (Å^3)": _format_tensor_value(delta[0, 0]),
                "dchi_xy (Å^3)": _format_tensor_value(delta[0, 1]),
                "dchi_xz (Å^3)": _format_tensor_value(delta[0, 2]),
                "dchi_yy (Å^3)": _format_tensor_value(delta[1, 1]),
                "dchi_yz (Å^3)": _format_tensor_value(delta[1, 2]),
                "dchi_zz (Å^3)": _format_tensor_value(delta[2, 2]),
                "chi_x (Å^3)": _format_tensor_value(eigvals[0]),
                "chi_y (Å^3)": _format_tensor_value(eigvals[1]),
                "chi_z (Å^3)": _format_tensor_value(eigvals[2]),
                "alpha (degrees)": _format_tensor_value(point.latents.alpha_deg),
                "beta (degrees)": _format_tensor_value(point.latents.beta_deg),
                "gamma (degrees)": _format_tensor_value(point.latents.gamma_deg),
            }
        )

    fieldnames = list(rows[0].keys())
    comments = ["paranmr/simpnmr-compatible susceptibility tensor series"]
    metadata_comment = _build_series_metadata_comment(series)
    if metadata_comment is not None:
        comments.append(metadata_comment)
    write_csv_rows_safe(
        file_name=path,
        fieldnames=fieldnames,
        rows=rows,
        comment=comments,
    )
    logger.info("Tensor series written to %s", str(path))


def _format_temperature(value: float) -> str:
    return f"{float(value):.2f}"


def _format_tensor_value(value: float) -> str:
    return f"{float(value):.6f}"


def _build_series_metadata_comment(series: TensorSeries) -> str | None:
    metadata = series.metadata
    required_keys = (
        "chi_iso",
        "chi_ax",
        "rho_over_ax",
        "alpha_deg",
        "beta_deg",
        "gamma_deg",
    )
    if any(key not in metadata for key in required_keys):
        return None

    seed = metadata.get("seed", "None")
    return (
        f"seed={seed}, "
        f"chi_iso={metadata['chi_iso']}, "
        f"chi_ax={metadata['chi_ax']}, "
        f"rho_over_ax={metadata['rho_over_ax']}, "
        f"alpha_deg={metadata['alpha_deg']}, "
        f"beta_deg={metadata['beta_deg']}, "
        f"gamma_deg={metadata['gamma_deg']}"
    )
