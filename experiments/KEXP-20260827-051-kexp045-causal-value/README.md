# KEXP-20260827-051 — KEXP-045 causal value audit

Status: **COMPLETE — DISTRIBUTION-SENSITIVE / DO NOT GENERALIZE FROM DEVELOPMENT**

## Question

KEXP-045 replicated W/L on both open distributions, but exploratory mean terminal delta was nearly neutral. This experiment isolates whether the two CARROT conversions themselves improve the candidate farm and/or alter the opponent through market externality.

## Protocol

For every development and exploratory live-meta environmental seed, both candidate seats, run paired worlds:

- A: KEXP-045 vs frozen R4B;
- B: frozen R4B vs frozen R4B.

Compare same-seat own terminal reward, opponent terminal reward and relative reward. Record exact conversions at 614→615 and 619→620.

Interpretation is causal only for the bounded KEXP-045 intervention because worlds are identical until the intervention. No validation or held-out seeds are accessed.

Tool: `tools/audit_kexp045_causal_value.py`  
Frozen tool blob: `f7070d5d0414dd2dc01d5824ac8224ebebf3b718`.

## Result

Run: `33048625512` — **SUCCESS**.  
Artifact: `9637207588`; ZIP SHA-256 `db099a5135f0282c3f86489dd291e598fb9b3a3c68927eace0e2bde3289f0290`.

Across all 72 paired worlds there were zero errors. The intervention triggered in 36 worlds.

### Development distribution

- triggered worlds: 22;
- mean own terminal delta: **+270.14**;
- median own delta: **+104**;
- positive own-delta fraction: **81.8%**;
- mean relative delta: **+240.73**.

### Exploratory live-meta distribution

- triggered worlds: 14;
- mean own terminal delta: **+9.29**;
- median own delta: **+34**;
- positive own-delta fraction: **57.1%**;
- mean relative delta: **−3.0**.

## Decision

The CARROT intervention has real causal value on the development distribution, but that value almost vanishes on the independent live-meta environmental distribution. This is direct evidence that the apparent late-CARROT edge is strongly distribution-sensitive.

KEXP-051 therefore does **not** justify extrapolating development gains to the hosted ladder. Any successor must be stress-tested on fresh environmental distributions before validation or hosted calibration.
