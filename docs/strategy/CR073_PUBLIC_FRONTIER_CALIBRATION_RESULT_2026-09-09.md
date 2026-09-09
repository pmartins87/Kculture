# CR073 public-frontier calibration — result

Date: 2026-09-09
Run: `34375720582`
Reference: `kaggle-environments==1.32.7`, both seats, fresh master seed `9092031`.

## Pre-registered question

Does exact local H2H against Kculture PARENT/PRESALE1 preserve the hosted-strength ordering of recent public agents with reported Kaggle scores around 2700–2990?

Decision rule was frozen before results:

- if a hosted-strong public agent scores >= 0.60 against both controls, use local decomposition of the strongest as a strategic guide;
- if multiple hosted-strong public agents are ~0.50 or lose locally despite high hosted strength, the local H2H is rejected as a global hosted-strength estimator and retained only for mechanics, causal ablation, regression and package parity;
- ambiguous evidence permits at most one targeted expansion.

## Decisive observed results

Three independent hosted-strong public architectures all produced the same extreme local result, with zero runner errors:

| Public agent | Reported hosted/public strength | vs PARENT | vs PRESALE1 |
|---|---:|---:|---:|
| Rayk V11 | ~2990.4 | 0-64 | 0-64 |
| Moon V11 | ~2736 | 0-64 | 0-64 |
| Multi-Route V59 | ~2767.3 | 0-64 | 0-64 |

That is 384/384 local losses across six H2Hs. Both seats were exercised. The result is not an engine/runtime error signal: jobs completed successfully and the exact-reference runner reported zero errors.

Indar V1 was still finishing when this methodological decision became mathematically unnecessary; its result is retained for the final CR073 aggregate but cannot reverse the decision above.

## Conclusion

**STRATEGIC_LOCAL_PROXY_FALSIFIED.**

The exact local laboratory remains trusted for what parity actually establishes: legal execution, deterministic mechanics, causal component tests, regression protection, seat safety and package/source parity. It is **not** a trustworthy estimator of global Kaggle ladder strength or final Bradley–Terry performance when the opponent distribution differs from the hosted metagame.

A Kculture policy that exploits one family locally can dominate a high-rated hosted strategy head-to-head while still being materially weaker against the real population. Therefore “beats high-score public agents locally” must not be used as a promotion gate going forward.

## New strategic hierarchy

1. **Hosted/live evidence and current official episode meta** — primary strategic calibration.
2. **Exact local causal tests** — establish whether a proposed mechanism actually causes the intended behavior and does not regress mechanically.
3. **Broad local H2H** — diagnostic only; never sufficient by itself for hosted promotion.
4. **Money margin** — diagnostic only.

## Next pre-defined step

Launch **CR074 — Current Hosted Meta Atlas** from the official public `kaggle/kaggriculture-episodes-index`, selecting the latest available daily episode datasets dynamically rather than hard-coding dates.

CR074 is descriptive/diagnostic only. It may nominate an architectural hypothesis only if the same winner-vs-loser directional signal appears in at least two recent dates. No strategy candidate is built from a one-day correlation.

The hosted submission `56124705` (CR071M PRESALE1) continues independently as a real-platform calibration probe.
