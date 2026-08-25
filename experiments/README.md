# Experiments — Kculture

Store promoted experiment summaries and lightweight reproducibility artifacts here.

Recommended layout:

`experiments/KEXP-YYYYMMDD-NNN-short-name/`

Each promoted experiment should contain at least:

- `README.md` — hypothesis, setup, result, decision
- `config.*` — exact strategy parameters when applicable
- `metrics.*` — machine-readable matchup/tournament summary when applicable
- references to larger episode logs or external artifacts when they cannot live in Git

Prefer compact summaries over committing huge raw episode logs. Preserve enough information to reproduce the experiment exactly.
