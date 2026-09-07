# Hosted calibration — 2026-09-07 — CR052 / CR053

## User-observed near-stable hosted ratings

- **CR052** — submission `56073867` — exact `Adaptive Route Agent V2` public package — approximately **1703**.
- **CR053** — submission `56073870` — static route from episode `106309334`, source seat 1 — approximately **2090**.

These values were read from the live Kaggle Game History UI by the user after both agents had accumulated substantial games. Treat them as near-stable snapshots, not immutable final scores.

## Pre-hosted evidence

### CR052

Exact archive SHA-256:
`b650a31d091323f2510aede0265937d3193a82a99109eadc8ab39c6e85db278d`

Local L1 versus CR029:
- 512 games;
- 130 wins / 328 ties / 54 losses;
- score rate 57.42%;
- mean margin +109.79;
- zero execution errors.

Hosted result: ~1703.

### CR053

Archive SHA-256:
`095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`

Fresh static validation versus CR029:
- 2048 games;
- 1268 wins / 780 losses;
- score rate 61.91%;
- mean margin +988.63;
- median margin +4739.

Hosted result: ~2090.

## Strategic calibration

**Candidate-vs-CR029 is no longer a sufficient promotion proxy.**

The same local gate ranked both CR052 and CR053 above CR029, yet hosted reality separated them by roughly 387 rating points, with CR052 returning to the old ~1700 band and CR053 advancing to ~2090. Other public high-score agents have also looked poor in CR029-only L1 screens.

From this point:

1. Hosted evidence outranks CR029 H2H when they conflict.
2. CR029 is one opponent in a league, not the tournament proxy.
3. Materially different public agents with strong hosted histories may deserve exact-copy hosted calibration even when CR029 H2H is negative.
4. New internal promotion should use a broad executable-agent league plus hosted calibration, not a single reference opponent.
5. Preserve theory diversity: static-route, state-adaptive, market-adaptive, pasture/economy and planner-like families should compete in parallel.

## CR057 current-hosted forensic snapshot

A 16-episode latest-window audit found:

- CR053: 5 wins / 11 losses against opponents concentrated around the ~2k band; its hosted action stream matched the exact frozen route tape with zero observed mismatches.
- CR052: 12 wins / 4 losses in the sampled latest window, but against generally lower-rated opponents; therefore raw latest W/L does not contradict its ~1703 rating.
- Offline CR052 package replay did not reproduce the recorded hosted action stream under the first simple replay harness, so that parity check is **inconclusive** rather than evidence of a bad upload. The exact archive itself was independently hash-verified before submission.

## Immediate external calibration pair

Prepared exact-source hosted candidates:

- CR055 — Preempt H6 V1 exact archive — SHA-256 `9c632b48239e96a23d2763a8f29081f46eb652b0bd2a6a455c6331fe57b81333`.
- CR056 — Indar `Shape the Shop Work the Pasture (TOP 10)` V1 exact archive — SHA-256 `fa9e7eb1a0174a1bf292fb4d47bd209defed929758214d3506e050a68ee5f98f`.

Purpose: hosted falsification/calibration of the local proxy. These are not CR029 derivatives.
