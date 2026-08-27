# KEXP-20260827-034 — mechanics-first late crop value margin

Status: **COMPLETE / FROZEN TRIGGER REJECTED / ROUTE-VALUE STRUCTURE FOUND**

## Why this follows KEXP-029/031

KEXP-029 and KEXP-031 showed that action imitation is not temporally stable enough to justify a deployable CARROT rule. KEXP-034 moved the crop branch from predicting what a top agent buys to estimating whether a WHEAT slot has positive counterfactual economic value if converted to CARROT.

No top-player action labels are used.

## Frozen protocol

Unchanged `R4B-market-only-validated-v1` vs deterministic `starter` on all 16 development seeds and 20 exploratory live-meta environmental seeds, with corrected replay alignment (`state t -> action frame t+1`).

Only KEXP-023 mechanically clean WHEAT plant windows are audited: 614–618, 620–623 and 636–647.

For each observed WHEAT plant, the same same-tile WATER/FERTILIZE/HARVEST schedule is replayed on a counterfactual CARROT tile using exact frozen engine mechanics. Actual R4B WHEAT `yield_units` immediately before HARVEST are retained as baseline.

## Canonical result

Actions run **`33042783455` — SUCCESS**.  
Artifact **`9634572686`**, ZIP digest **SHA-256 `f6fc9726e0a5b85d71190f38cd4128e856b8351f94b02fb1384d7a4a40848b7a`**.

Total audited safe WHEAT slots: **616**.

Development:

- 272 events across 16 episodes;
- fixed `+20` simple-proxy trigger: **0 events / 0 episodes**;
- median R4B WHEAT seed buys during 600–635: **13**.

Exploratory live-meta:

- 344 events across 20 episodes;
- fixed `+20` trigger: **19 events, all in one episode**;
- all 19 had positive future-price oracle margin;
- mean oracle margin **+345**, median **+380**;
- median R4B WHEAT seed buys during 600–635: **13**.

Combined, the trigger appeared in only **1/36 episodes**. The predeclared support gate therefore fails decisively.

### Stronger mechanics finding

The counterfactual simulation exposed a much more useful structural fact than the failed trigger:

- in the earlier safe-route events, actual WHEAT and same-route CARROT yield were **3 vs 3**;
- in the later safe-route events, they were **2 vs 2**;
- CARROT survived the copied route in **616/616 events**.

Across the observed safe-route support, WHEAT and CARROT therefore have equal same-route unit yield. The relevant current-price economic comparison is not the deliberately pessimistic original proxy `3*CARROT - 20 - (4*WHEAT - 10)`. For an audited route with equal yield `q`, it reduces mechanically to:

`q * (CARROT_price - WHEAT_price) - 10`

where `10` is the additional CARROT seed cost.

The exact same-route current-price margin was strongly aligned with the later harvest-price oracle in this audit; this is a diagnostic observation, not permission to tune a new threshold on the same data.

## Decision

The **predeclared +20 trigger is rejected**. Do not tune that threshold after seeing the result.

The crop branch remains active because KEXP-034 discovered a simpler exact route-value structure. The next step should be a bounded value/rollout controller that:

1. uses exact mechanically expected route yield rather than generic crop maxima;
2. prices WHEAT vs CARROT from legal current public state;
3. explicitly reallocates existing WHEAT seed purchases because KEXP-026 proved no idle CARROT stock exists;
4. caps substitutions and evaluates actual W/L rather than action-imitation accuracy.

No validation or held-out seeds were accessed. Opponent/team/episode/seed identity remains forbidden as a deployable feature.

Tool: `tools/audit_late_crop_value_margin.py`  
Frozen tool blob: `bdb99ef47251f9d3a8d46bb923d4eea0f13c38d1`
