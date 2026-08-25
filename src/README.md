# Source architecture — Kculture

Implementation should evolve toward modular strategy components with a thin Kaggle entrypoint.

## Intended modules

- observation/state adapter
- legal-action and no-op guard
- path/movement planner
- economy/value model
- crop planner
- livestock planner
- labor/farm-hand planner
- expansion planner
- market model
- opponent model
- tactical action scheduler
- policy/strategy configuration
- episode logger
- Kaggle packaging layer exposing `agent` from root `main.py`

## Design constraints

- deterministic fallbacks for unexpected states
- explicit random seeds where randomness is used
- no invalid/crash-prone action paths
- separation between official mechanics and learned/inferred models
- cheap-enough per-turn decision logic for hosted execution
- strategy parameters externalized when practical for automated search

No competition agent code has been added yet. Import/version the official environment and starter assets before implementing the first baseline.
