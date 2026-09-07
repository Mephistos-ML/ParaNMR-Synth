# paraNMR-Synth

`paraNMR-Synth` is a standalone generator of magnetic susceptibility tensor series for paramagnetic NMR simulation workflows and machine-learning datasets.

The package is built to generate physically valid, temperature-dependent susceptibility tensors in a format that can be consumed by `paranmr/simpnmr`. Its immediate value is upstream of simulation: it gives ML workflows a controlled way to sample tensor trajectories with explicit latent parameters, temperature grids, and reproducible seeds.

## Why this library matters for ML

In paramagnetic NMR, the magnetic susceptibility tensor is a compact physical object that strongly controls PCS-driven spectral behaviour. For ML applications, that makes it a useful representation layer:

- physically meaningful
- lower-dimensional than spectra
- easy to constrain
- easy to sample reproducibly
- directly consumable by downstream simulation tools

Instead of starting from broad synthetic artifacts and inferring structure afterward, `paraNMR-Synth` starts from the tensor itself. That makes dataset generation more controlled, more interpretable, and easier to audit.

Typical use cases:

- synthetic data generation for inverse pNMR problems
- supervised learning on latent-to-tensor mappings
- augmentation across temperature series
- benchmarking tensor reconstruction models
- generating `paranmr/simpnmr`-compatible inputs at scale

## Current scope

Version `v0.0.1` is intentionally focused.

Implemented:

- `iso / ax / rho_over_ax` tensor parameterization
- one shared orientation per generated series
- integer temperature grids
- Curie-like temperature dependence across the series
- deterministic YAML-driven generation
- `paranmr/simpnmr`-compatible CSV export
- CLI entrypoint for reproducible batch generation

Not implemented yet:

- alternative tensor parameterizations
- richer temperature-dependence models
- dataset manifests and metadata bundles
- dedicated ML dataset export layers

## Installation

```bash
python3 -m pip install -e .
```

For development:

```bash
python3 -m pip install -e .[dev]
```

## Quick start

Example config:

```yaml
output_name: run_minimal_output

generator:
  n_series: 1
  seed: 7

temperature:
  start: 280
  stop: 282
  step: 1

chi_iso: 10.0
chi_ax: 3.0
rho_over_ax: 0.1666666667

orientation:
  alpha_deg: 0.0
  beta_deg: 0.0
  gamma_deg: 0.0
```

Run:

```bash
paranmr-synth run examples/run_minimal.yaml
```

This creates:

```text
examples/run_minimal_output/
  susceptibility_tensor_1_280K_to_282K.csv
```

## YAML contract

The input model is intentionally small.

Scalar values mean fixed parameters:

```yaml
chi_ax: 3.0
```

Two-element lists mean uniform sampling bounds:

```yaml
chi_ax: [0.0, 3.0]
```

The same pattern applies to Euler angles:

```yaml
orientation:
  alpha_deg: [0.0, 360.0]
  beta_deg: [0.0, 180.0]
  gamma_deg: [0.0, 360.0]
```

`output_name` controls the name of the folder created next to the YAML file.

If `output_name` is omitted, the folder name defaults to the YAML filename stem.

## Output contract

Each generated CSV stores one full temperature series of susceptibility tensors.

The exported layout is compatible with `paranmr/simpnmr` and includes:

- temperature
- `chi_iso`
- `chi_ax`
- `chi_rho`
- full Cartesian tensor components
- traceless anisotropic components
- principal values
- Euler angles

That makes the generator useful both as a standalone library and as an upstream source for pNMR simulation pipelines.

## Physical and engineering constraints

The library validates a small set of explicit invariants:

- `0 <= rho_over_ax <= 1/3`
- Euler angles in valid `ZYZ` ranges
- symmetric `3x3` susceptibility tensors
- positive temperatures
- strictly increasing temperature series without duplicates
- sampling bounds with `lower <= upper`

These checks live in the core constraint layer rather than being scattered across CLI or config parsing code.

## Architecture

The package is structured as a layered system:

```text
src/paranmr_synth/
  app/    # orchestration
  cfg/    # YAML-facing config loading
  cli/    # command-line entrypoint and logging
  core/   # constraints, domain, generators, parameterizations, rotations
  io/     # export adapters
```

Responsibilities are separated on purpose:

- `cli` handles user interaction
- `cfg` translates YAML into typed internal specs
- `core` owns scientific and numerical logic
- `io` owns file-format boundaries
- `app` wires the pipeline end to end

This keeps the codebase usable both as a CLI tool and as a library component inside larger ML and simulation workflows.

## Reproducibility

Generation is seed-controlled:

```yaml
generator:
  n_series: 100
  seed: 42
```

That matters for ML dataset work, where exact regeneration of sampled tensors is often required for experiments, benchmarks, and audits.

## Relationship to paranmr/simpnmr

`paraNMR-Synth` is not meant to replace ParaNMR. It sits upstream of that ecosystem.

- `paraNMR-Synth` generates susceptibility tensor series
- ParaNMR consumes susceptibility tensors in fitting and simulation workflows

That separation is useful. One tool is responsible for controlled data generation; the other is responsible for domain simulation and analysis.

## Development

Run tests:

```bash
PYTHONPATH=src python3 -m pytest -q
```

Run the example:

```bash
paranmr-synth run examples/run_minimal.yaml
```

## Roadmap

Planned next directions:

- broader prior families for tensor latents
- additional tensor parameterizations
- richer temperature-dependence models
- dataset provenance and metadata export
- tighter support for larger synthetic ML corpora

## License

MIT
