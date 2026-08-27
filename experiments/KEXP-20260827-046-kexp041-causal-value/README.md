# KEXP-20260827-046 — causal value decomposition of KEXP-041

Status: **RUNNING / DIAGNOSTIC ONLY**

## Question

KEXP-041 beat R4B 20-12 on development but replicated only 14-14-12 (score 0.50, mean -21.35) on exploratory live-meta environmental seeds.

This experiment asks whether the bounded CARROT mutation still has positive causal value for our own farm outside development, with W/L neutrality arising from market/opponent externality, or whether the mutation itself loses value.

## Paired-world protocol

For every development seed and exploratory live-meta environmental seed, in both candidate seats, run:

- World A: KEXP-041 vs frozen R4B;
- World B: frozen R4B vs frozen R4B.

The two worlds are identical before KEXP-041's only intervention at state 614. For each seat/seed record:

- whether exact BUY+PLANT mutation occurred;
- own reward change relative to same-seat R4B counterfactual;
- opponent reward externality;
- change in relative terminal margin.

Primary interpretation is restricted to triggered games. Quiet games should have near-zero differences and act as a parity check.

## Decision use

- If triggered own causal delta is positive in both pools but relative delta fails in live-meta, next controller must include opponent/market externality.
- If own causal delta itself is non-positive in live-meta, one-step current-price value is insufficient and the crop controller needs richer lifecycle/forecast value.
- If quiet games differ materially, diagnose implementation/state leakage before further strategic conclusions.

No threshold fitting, validation or held-out access.

Tool: `tools/audit_kexp041_causal_value.py`  
Frozen tool blob: `f7622d498422eb4714850dffd08eb00c2bbf54a2`.
