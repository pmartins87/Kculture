# ROADMAP — Kculture live plan

Updated: 2026-09-13

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, `STATUS.md`, and frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before validation results are interpreted.
4. Invalid evaluations are quarantined; their scores are not strategy evidence.
5. No seed, team identity, EpisodeId, future state or opponent-private state as runtime features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune a failed architecture on spent validation evidence; change representation instead.
9. Strong local H2H against CR071M/legacy anchors is necessary but not sufficient for hosted metagame value.
10. Future promotion requires an independent high-strength population proxy before a hosted slot is spent.
11. **Do not enter polling loops.** Live state is checked only at predeclared/material decision boundaries.

## Closed architecture classes

- CR078 late mirror breaker.
- CR079 SpaTaro 1-NN.
- CR080 replay/route stitching.
- CR081 time-indexed market transplant.
- CR082 same-step state-conditioned teacher 1-NN.
- CR084 critical late-livestock rescue — promotion FAIL; no retuning.
- CR085 public-Pareto gated adaptive switch — Gate A FAIL; no retuning.

Behavioral imitation remains closed. Public replays/code may be used to benchmark architectures and discover legal state/regime mechanisms, not to create identity-conditioned runtime policies.

## ACTIVE — CR083 hosted maturation

Frozen candidate SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**.

Kaggle submission: **`56199767`**.

Latest authenticated checkpoint already obtained in this work session:

- CR083: **1660.3**;
- CR071M: **1638.8**;
- observed CR083 lead: **+21.5**;
- about **76 public completed episodes** plus validation.

Frozen maturity rule remains: no final hosted verdict before 100 public completed episodes, and no repeated polling before that boundary.

## CLOSED — CR084

Final record: `docs/strategy/CR084_FINAL_RESULT_2026-09-13.md`.

Corrected frozen SHA: `3aa08bb2ee163d1707dbf0bf9d2cb4b6f8c194fa2dbd715c38a67a4a41d414a2`.

Promotion master `9140842`: CR084 vs CR083 **12W–10L–42T = 0.515625**, mean margin `-106.625`; temporal high-strength proxy found zero rescue opportunities. Decision: `CLOSE_CR084_CRITICAL_FEED_RESCUE`.

## CLOSED — CR085

Frozen SHA: **`eb7bac5c5619e70d1ef81dd18f28b642b96326be31ae50354cdca7770531bdf7`**.

Gate A run `34761593920`, master `9150851`:

- exact 32 games / 16 fresh seeds;
- zero errors / zero non-DONE;
- **3W–3L–26T = 0.5000** versus CR083;
- mean terminal-money margin **-147.46875**;
- semantic audit PASS and seed firewall PASS.

Decision: `CLOSE_CR085_PARETO_GUARDED_SWITCH`.

Do not tune its money/animal/plant dimensions, guarded steps 360/433, or zero-threshold Pareto rule.

## NEXT — CR086 strong-backbone discovery

The project now pivots away from incremental CR083 route patches. Public competition notebooks currently include substantially stronger displayed agents, so the rational next step is to benchmark those implementations and extract architectural mechanisms before inventing another patch.

### Stage 1 — read-only public-source acquisition

Pull and freeze selected public Kaggle notebook sources, initially:

- `indarkarhana/shape-the-shop-work-the-pasture-top-10`;
- `boatlee/v29-r1-adaptive-market-hysteresis`;
- `lynnsakurai/farming-score-v3-replay-revised`;
- optionally the separate public `shape-the-shop-work-the-pasture` implementation if distinct.

For every source freeze:

- record owner/slug;
- preserve source files exactly;
- record SHA-256;
- record visible license/attribution metadata;
- never submit during acquisition.

### Stage 2 — architecture and executable-agent audit

For each public source:

1. locate or reproduce the exact agent packaging path only when the public source itself makes it available;
2. classify architecture: static route/tape, market adaptation, hysteresis, search/planning, state estimation, terminal liquidation, etc.;
3. verify runtime legality and remove any benchmark that depends on forbidden/private information;
4. exact-H2H benchmark unmodified executable public agents against CR083 first, then legacy anchors where useful;
5. do not call a public agent CR086 merely because it wins locally.

### Stage 3 — quantitative adversary-state layer

In parallel, investigate the public-state opponent inventory estimator discussed by a current top competitor. The key representation is an estimate/range of opponent commodity stock derived from market inventory deltas, public harvest/consumption and known mechanics, with uncertainty for price-floor sales, overflow, DROP and ambiguous transitions.

The intended runtime representation is legal current/public state only:

- `opponent_inventory_estimate[commodity]`;
- lower/upper bounds;
- uncertainty / floor-sale / private-loss risk flags;
- derived market-pressure and liquidation-risk features.

No opponent identity/rating, hidden seed, future state or private observation.

### Stage 4 — freeze CR086 only after evidence

CR086 protocol may be frozen only when one of two routes has evidence:

A. a public strong backbone materially dominates CR083 locally and has a compliant license/attribution path, then we add a genuinely independent legal value layer; or

B. public architectures identify a mechanism that can be cleanly reimplemented in our own code and materially outperforms CR083 in a fresh benchmark.

Any CR086 hosted probe still requires:

1. fresh direct improvement versus incumbent;
2. legacy guardrails;
3. independent high-strength population stress;
4. licensing/attribution audit if public code contributes to the candidate.

## Frontier targets

Latest top-10 read-only checkpoint already obtained in this work session:

1. Majkel1337 `3239.9`
2. Mengfei Li `3065.9`
3. Artem The Farmer `3064.4`
4. ymg_aq `3020.9`
5. SpaTaro `3019.2`
6. Otter Vibe `3005.0`
7. redblackbst `2991.3`
8. feel the agi `2990.5`
9. binghua `2968.2`
10. Subramanya N `2965.4`

The target remains ~3000-class performance, not merely beating a mid-1600 incumbent.

## Escalation rule

A new architecture earns a hosted probe only after passing three independent performance layers plus a provenance check:

1. fresh direct improvement versus the incumbent backbone;
2. broad legacy-anchor guardrails;
3. frozen high-strength population-regime stress evidence;
4. public-code provenance/license compliance where applicable.

If hosted evidence contradicts the first two layers, improve the proxy/representation instead of retuning a spent mechanism.
