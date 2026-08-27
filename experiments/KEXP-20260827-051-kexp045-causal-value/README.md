# KEXP-20260827-051 — KEXP-045 causal value audit

Status: **RUNNING / DIAGNOSTIC**

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
