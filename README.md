# ParaNMR-Synth

`ParaNMR-Synth` generates deterministic, replayable synthetic pNMR datasets for supervised learning and validation of ParaNMR fitting workflows.

Each synthetic case contains a ParaNMR-ready fixed-assignment fit input and hidden synthetic truth. The dataset root also contains one paired ML table:

```text
dataset.csv
manifest.json
cases/<sample_id>/
  fit/
    config.yml
    geometry.xyz
    generated_shifts.csv
    diamagnetic.csv
  synthetic_output/
    susceptibility.csv
    linewidth.csv
```

`dataset.csv` is the canonical supervised-learning artifact. One row contains `m1..mN` as features and six Cartesian susceptibility components plus `p1,p2` as targets. The selected susceptibility unit is recorded in `manifest.json`. `synthetic_output/` is validation provenance, not an ML input.

## Requirements

The dataset pipeline requires ParaNMR with atom-labelled diamagnetic CSV input, fixed-assignment `linewidth: estimate: p1_p2`, and ParaNMR experiment CSV round-tripping.

```bash
python3 -m pip install paranmr
python3 -m pip install -e .[dev]
```

## Dataset YAML

```yaml
project:
  name: ybl8_moments_v1
  n_cases: 1000
  seed: 42
hyperfine:
  method: pdip
  file: geometries/YbL8.xyz
  paramagnetic_centre: [0.0, 0.0, 0.0]
  spin: 0.5
  orbit: 3
  total_momentum_J: 3.5
nuclei:
  include: H
diamagnetic:
  range_min_ppm: 0.0
  range_max_ppm: 10.0
experiment:
  temperature_k: 302.15
  magnetic_field_t: 4.7
moments:
  number_of_moments: 10
linewidth:
  method: r6
  variables:
    p1: [500.0, 2000.0]
    p2: [0.0, 1.0]
susceptibility:
  model: isoaxrho_euler
```

`chi_iso` is calculated through ParaNMR's spin-only Curie-law implementation.
Synth samples `rho_over_ax` in `[0, 1/3]`, derives physical bounds for
`chi_ax`, and samples Euler angles in their canonical ZYZ domains. All χ
targets are exported in canonical ParaNMR units of Å³.

## CLI

```bash
paranmr-synth dataset generate ybl8.yml --output datasets/yb_v1
cd datasets/yb_v1/cases/<sample_id>/fit
MPLBACKEND=Agg paranmr --hide fit_susc config.yml
paranmr-synth dataset validate ../
```

`validation_report.json` records truth, fitted values and errors. It does not silently reject a sample based on rank, condition number or score.

## Validation stages

The replay profile uses ParaNMR fixed assignment. It validates the forward data contract and separately recovers R6 `p1,p2` from labelled linewidths. Assignment-free GMM moments validation belongs to ParaNMR's own synthetic test suite and is intentionally a later stage.

## Development

```bash
python3 -m pytest -m 'not integration'
python3 -m pytest -m integration
```

The integration suite launches the real `paranmr` executable and must run against the compatible ParaNMR version. Every generated CSV records `ParaNMR-Synth` version provenance in its comment header.
