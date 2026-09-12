# CR083 — explicit economic-value architecture boundary

Status: **conditional successor boundary, frozen before CR082 H2H results are interpreted**.

This document does not authorize a CR083 executable yet. It exists to prevent a failed CR082 from being cosmetically retuned on spent validation evidence.

## Activation

CR083 activates only if the canonical frozen CR082 H2H workflow `34708795892` fails its pre-registered promotion gate.

If CR082 passes, follow CR082's hosted-probe path first; do not use this document to delay the probe.

## Architecture class that is closed if CR082 fails

A CR082 failure closes **behavior imitation by same-step nearest-neighbor teacher selection** for this validation generation. Therefore CR083 may not be any of the following disguised variants:

- CR082 with a different `k`;
- feature addition/removal/reweighting chosen after seeing master `9120821`;
- a different OOD percentile;
- a different 0–287 boundary;
- a different subset of Majkel teacher episodes;
- nearest-neighbor imitation of UMG, ymg_aq or another named leader;
- mixtures/votes of teacher actions whose principal signal is still behavioral similarity;
- replay continuation, trajectory stitching, team identity, EpisodeId, seed, future state or opponent-private information.

Master `9120821` is permanently spent for CR083 candidate selection.

## Required conceptual change

CR083 must select economic actions from **estimated value under the current legal game state and game mechanics**, not from the identity of the action a teacher happened to take in a similar state.

The action space may still use legal economic macros observed in the game grammar (`SELL`, `BUY_PRODUCT`, `BUY_SEED`, `HIRE`, `BUY_ANIMAL`, `BUY_LAND`, and empty/no-op market action), but their ranking must come from an explicit value/objective model.

Examples of admissible value components, subject to a mechanics audit before freezing a candidate, include:

- immediate cash-flow effect;
- inventory liquidation value at public prices;
- productive-capacity effect of seeds/animals/land/labor;
- shed/capacity pressure and legality;
- remaining-horizon opportunity cost;
- public-price/inventory scarcity effects;
- short-horizon state transition value when the exact environment mechanics support reproducible counterfactual branching.

Teacher/frontier replays may be used to discover **which legal macro families deserve evaluation** and to calibrate state distributions, but not as the runtime nearest-neighbor action oracle.

## Mandatory Phase 0 before any CR083 candidate

Before choosing a value formula or learner, audit the exact `kaggle-environments==1.32.7` Kaggriculture mechanics and establish which counterfactual operations are reproducibly available from legal current state.

Phase 0 must document:

1. economic action legality and execution order;
2. cash and inventory effects of every market action family;
3. shed/capacity accounting;
4. seed/animal/land/labor productive effects and timing;
5. what parts of the transition are deterministic versus seed/randomness dependent;
6. whether exact arbitrary-state cloning/branching is possible without hidden/future information;
7. a leakage audit showing that every runtime feature/action score is computable from legal current observation plus frozen mechanics/constants.

If arbitrary-state exact branching is not valid, CR083 must use a mechanics-derived surrogate value model rather than pretending counterfactual replay is causal.

## Evidence discipline

- Do not inspect or optimize CR083 on CR082 master `9120821`.
- Original final holdout remains sealed.
- Any exploratory corpus already used to formulate CR083 becomes hypothesis-forming only.
- Before a CR083 executable exists, freeze its representation, training/calibration split, Gate A evidence source, and promotion thresholds.
- A CR083 candidate must use a new non-overlapping seed master.

## Goal

The desired representation shift is:

`what did a leader do in a nearby state?`

→

`which legal economic macro has the highest estimated value in this state, given the mechanics and remaining horizon?`

That is the required architectural novelty if CR082 fails.
