# Public methods → Kculture architecture requirements — 2026-08-25

## Purpose

Translate publicly disclosed Kaggriculture methodology into auditable design requirements without claiming or copying unpublished/private code. This document is architectural research, not evidence that a particular implementation reproduces another contestant's policy.

## Public methodology signals

### Kaito Fukami — v18 Closed Loop

Public notebook: `https://www.kaggle.com/code/kaitofukami/40-53-top-10-future-holdout-v18-closed-loop`

The public notebook's table of contents explicitly frames the approach around:

1. why a previous policy became weak quickly;
2. a **coherent board, closed-loop market** policy;
3. optimizing **winning rather than action imitation**;
4. a **walk-forward split across teams, time, and seats**;
5. **ablations** to reject decorative complexity;
6. a separation between learned and fixed components;
7. a public-source/copy contract;
8. explicit limitations and an update rule.

The page is Apache-2.0. The headings are useful methodological evidence even before exact source acquisition.

### Current Kaito reference

`25/27 Strict-Future | v27 Midgame Meta Reset`, exact public target V4, had a 3090.1 score snapshot when inspected on 2026-08-25. Its title itself signals later evolution toward strict-future evaluation and midgame adaptation. Treat the score as dynamic discovery metadata, not a guaranteed ceiling.

### Andrew Sokolovsky — Breaking the Tie

Public notebook: `https://www.kaggle.com/code/andrewsokolovsky/kaggriculture-breaking-the-tie`

The inspected page is Apache-2.0 and showed a best-score snapshot of 2915.2 at V12. A recent public build log explicitly checked `same-turn DROP credit`, importability and compilation before packaging. This reinforces the need for execution-order correctness around terminal logistics.

## What this implies for Kculture

### A. Closed-loop market state must become first-class

R4A is fundamentally a strong routed/open-loop economic tape with bounded recovery and some public-state adaptation. R5 should instead maintain a compact state estimator on every turn:

- current market prices and inventory by product;
- town shops/demand currently unlocked;
- own shed, unit inventories and immediately executable stock;
- public opponent farm composition;
- recent own sale quantities and resulting price response;
- whether the current production mix is still economically aligned with observed demand.

The controller should re-evaluate economic decisions from current state rather than merely replaying a previously selected route whenever a safe adaptation point exists.

### B. Board policy and market policy must be coherent

A market controller cannot repair a production plan that structurally creates the wrong inventory. R5 should couple:

- target animal/crop mix;
- land expansion timing;
- hand count and labor assignment;
- expected harvest/animal-output cadence;
- market sale timing.

A proposed market adaptation should be rejected when the board cannot supply it in time. A proposed board adaptation should be rejected when its expected output has no plausible demand/value path before the horizon.

### C. Winning is the objective

Official Kaggriculture rating reacts to win/loss/tie, not the coin margin itself. Therefore:

- primary promotion metric: both-seat W/L/T or score rate;
- secondary diagnostics: money delta, terminal bank, runtime, product revenue, stranded stock and route-specific deltas;
- no candidate is promoted merely because average coins increase if its head-to-head score rate decreases.

This is already consistent with the R2/R4 tournament harness and should remain invariant through R9.

### D. Walk-forward means opponent/time leakage controls

Kculture's existing development/validation/held-out split handles random seed leakage but is not yet sufficient for a changing public meta. Future strong-opponent corpora should also be partitioned by acquisition time/version and architecture family.

Proposed rule:

- **development opponents**: versions already used to design the candidate;
- **future validation opponents**: later or independently acquired versions not used for design;
- **held-out promotion panel**: architecture families and exact versions frozen before the final candidate is selected.

Both seats remain mandatory. When replay-derived evidence is used, chronological ordering must be preserved so a candidate never receives future opponent behavior as a design feature for an earlier evaluation slice.

### E. Ablation before complexity

Every adaptive mechanism should have a paired ablation. Examples:

- R4B terminal optimizer vs identical R4A base;
- closed-loop price response ON vs OFF;
- public opponent-layout feature ON vs OFF;
- adaptive production reallocation ON vs fixed route;
- learned selector vs deterministic threshold with the same feature set.

A mechanism that cannot show robust incremental value on the same seeds/opponents should not be retained merely because it appears sophisticated.

## Proposed R5 architecture after R4 closes

`R5-stateful-economic-controller-v1` should be layered around a reproducible strong base:

1. **Observation normalizer** — exact public/private state that the rules permit us to see.
2. **Economic state estimator** — price/demand/inventory/production summaries and recent deltas.
3. **Board capacity model** — expected short-horizon production and labor availability.
4. **Action feasibility layer** — cash, seed, shed, land, actor-position and market-order constraints.
5. **Closed-loop economic policy** — choose among a small set of auditable interventions rather than free-form route rewrites.
6. **Safety/recovery layer** — preserve R4A's proven weed, purchase, placement, state-isolation and retry protections unless ablation proves a replacement safer.
7. **Terminal controller** — handle horizon-aware stop-investment/liquidation decisions as a distinct subsystem.

Initial interventions should be sparse and reversible, for example:

- preempt/retard a sale using visible current demand and price impact;
- adjust one future product family when public demand and own capacity jointly support it;
- alter a bounded animal/crop target at a shared-prefix/adaptation boundary;
- stop reinvestment earlier when remaining horizon cannot repay capital cost.

## R4B interpretation boundary

COK's V8 evidence says 57 of 59 recorded losses had lower **realized sale revenue after step 672** than the opponent. That is an observational late-game revenue deficit. It does **not** prove that stock was stranded at the final action or that global liquidation is the causal fix.

R4B therefore remains a clean causal experiment: it changes only step 718 and asks whether a capacity-aware final liquidation improves outcomes. If it fails, the next hypothesis should move upstream into supply/midgame adaptation rather than repeatedly tuning the terminal step.

## Promotion discipline

- Do not open validation until the R4B development decision is frozen.
- Do not open held-out until a formal promotion candidate exists.
- Exact public sources must be version-pinned and hashed before local opponent use.
- Preserve third-party licenses and provenance; do not attribute their policy code to Kculture.
- Public notebook scores are scouting signals, never substitutes for controlled local evidence.
