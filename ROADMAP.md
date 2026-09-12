# ROADMAP — Kculture live plan

Updated: 2026-09-12

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, `STATUS.md`, and current frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before valid validation results are interpreted.
4. Mechanically or semantically invalid runs are quarantined; their scores are not strategy evidence.
5. No seed, team identity, EpisodeId, future state or opponent-private state as agent features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune a failed architecture on spent validation evidence; change representation instead.

## Closed architecture classes

- CR078 late mirror breaker: closed.
- CR079 simple SpaTaro 1-NN: closed after OOT failure.
- CR080 nearest-route/day replay stitching: closed; economic-state aliasing.
- CR081 time-indexed UMG market transplant: closed after valid catastrophic H2H failure.
- **CR082 same-step state-conditioned teacher 1-NN: closed after valid catastrophic H2H failure.** Canonical run `34708795892`, master `9120821`, lost 0–64 directly to CR071M and 0–64 against all three guardrails despite zero execution errors. No CR082 retuning.

Combined conclusion: neither trajectory imitation nor current-state behavioral imitation establishes causal economic value for CR071M. The representation must change from `predict leader action` to `estimate value of legal action`.

## Current frontier

Authenticated snapshot `34668645531`: Majkel 3181.9, ymg_aq 3075.1, UMG 3056.5, Artem 3029.3, SpaTaro 3029.0.

## ACTIVE — CR083 explicit economic-value / macro selection

Architecture boundary: `docs/strategy/CR083_EXPLICIT_VALUE_ARCHITECTURE_BOUNDARY_2026-09-12.md`.

Phase 0 completed successfully in run `34709053070` with exact `kaggle-environments==1.32.7`:

- exact state cloning/branching is technically valid offline;
- terminal objective is final money;
- market execution order, capacity, prices, crops, animals, hires and land mechanics have been captured;
- future random shop unlocks depend on hidden seed and must be marginalized rather than exposed to runtime policy;
- opponent market actions are simultaneous/lockstep, so value research must predeclare an opponent assumption/mixture.

### Phase 1 — causal economic-family ablation

Before freezing a CR083 executable, determine which CR071M market-action families actually create value for its physical backbone.

Use a new fresh exploratory master, never `9120821`, and exact reference runtime. Construct mechanically identical CR071M variants that remove exactly one market family after all baseline safety logic:

- `SELL`;
- `BUY_SEED`;
- `BUY_PRODUCT`;
- `BUY_ANIMAL`;
- `HIRE`;
- `BUY_LAND`.

This is architecture research only, not a promotion gate. No hosted submission. The result chooses which economic mechanisms deserve explicit value modeling; it does not authorize tuning on its seeds.

### Phase 2 — explicit-value representation

After Phase 1:

1. preserve CR071M same-step farmer/hands backbone and proven safety transforms;
2. formulate value scores only for economic families implicated by the causal ablation;
3. use current legal observation + public mechanics/constants only;
4. if multi-step counterfactual labels are used, average/marginalize hidden future randomness across independent seeds rather than using replay seed clairvoyance;
5. handle opponent market uncertainty with a frozen structural-anchor mixture or robust objective;
6. pre-register representation, calibration data, Gate A and promotion thresholds before building the executable candidate.

### Promotion discipline

Any eventual CR083 candidate gets a new non-overlapping master and a frozen direct+guardrail panel. PASS can authorize one controlled hosted probe after authenticated slot accounting. FAIL changes representation again; no post-hoc threshold/feature tuning on spent seeds.

## Escalation rule

When a valid candidate passes a frozen fresh gate with material uplift, move to one controlled hosted probe rather than accumulating optional local tests. When it fails, change representation rather than optimize against spent validation seeds.
