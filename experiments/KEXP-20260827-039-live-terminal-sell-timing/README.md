# KEXP-20260827-039 — live terminal SELL timing

Status: **COMPLETE / OBSERVATIONAL SUPPORT ONLY**

## Question

KEXP-037 derives a mechanics-based argument for selling already-available non-input products at state 717 instead of waiting for 718. KEXP-039 independently checks how recent high-Elo public agents actually time terminal SELLs.

## Frozen protocol

Official top-20 episodes from 2026-08-23, 24, 25 and 26; corrected replay alignment `state t -> action frame t+1`; exact states 712..718.

## Canonical result

GitHub Actions run **33043640991 — SUCCESS**.  
Artifact **9634827281**, ZIP digest **SHA-256 `4fae13b15f5b174d15792ec312b52a8f133d205472835dac25146e318c324245`**.

Across 160 player-trajectories:

- total SELL qty at state 717: **1,617**;
- total SELL qty at state 718: **501**;
- 717 share of combined 717+718 quantity: **76.35%**.

Winners (80 trajectories):

- 717 qty 645;
- 718 qty 247;
- 717 share **72.31%**.

Losers (80 trajectories):

- 717 qty 972;
- 718 qty 254;
- 717 share **79.28%**.

By date, winners' 717 shares were 81.48%, 63.74%, 71.54% and 77.06% respectively. Thus selling before the last executable state is persistent across days, but **more 717 concentration is not a winner signature** in this sample.

The broader pattern is more important: strong agents liquidate continuously through 712..717 rather than relying on one huge state-718 dump. This supports treating market timing as a dynamic subproblem, while showing that KEXP-037's single-state front-run should be judged only by controlled W/L.

## Decision

No policy promotion comes from this observational experiment. KEXP-037 remains a small development-passing candidate pending its exploratory direct replication.

No validation or held-out seeds were accessed.

Tool: `tools/live_terminal_sell_timing.py`  
Frozen tool blob: `67487d740a5e2a3ac67a01e60c7d58b59d91a6e5`.
