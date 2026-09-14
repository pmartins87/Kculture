# FP001 ROADMAP — first-principles economy

Updated: 2026-09-14

Objective: produce a hosted-competitive zero-lineage Kaggriculture agent by deriving policy from game mechanics and runtime state rather than competitor replay imitation.

## Binding rules

- Official environment + our experiments define mechanics.
- Competitor replays may be evaluation opponents only, never teachers or route templates.
- Every stage needs a causal hypothesis and control/null where applicable.
- Use fresh seeds and both seats.
- No identity/rating/EpisodeId/hidden-seed/future/opponent-private runtime features.
- Do not rescue failed first-principles hypotheses with replay-derived routes.

## R0 — mechanics parity — PASS

Workflow `34842825909`.

## R1 — H1 town-pulse WHEAT carry — PASS

Workflow `34843184110`: +916.875 mean paired delta; flat-price null exactly zero. Preserve for later opportunity-cost integration.

## R1B — owned-inventory pulse sale deferral — PASS

Workflow `34843556192`: 104/104 positive exact cases. Preserve as sale-timing primitive.

## R2A — H8 animal/fertilizer economics — PASS

Workflow `34844070131`: large raw economics established.

## R2A2-A — exact FEED/CARE frontier — PASS

Workflow `34844616747`: abstract control favored SHEEP, proving species choice depends on action/horizon economics but not settling physical architecture.

## R2A2-B1 — one-animal runtime — PASS

Workflow `34844919444`: COW mean +4721, SHEEP +3593, GOOSE +3457. Physical runtime reversed the abstract species ranking.

## R2A2-B2 — multi-animal runtime — PASS

Workflow **`34846686427`**.

Mean realized deltas, 8 fresh seed/seat episodes each:

- **COW3_H0 +12880.75**;
- COW3_H2 +12824.75;
- COW2_SHEEP1_H2 +11881.0;
- COW1_SHEEP2_H2 +10874.75;
- SHEEP3_H2 +9807.0;
- COW2_H0 +8522.25;
- COW2_H2 +8465.0.

Labor ablation:

- COW2: H2-H0 **-57.25**;
- COW3: H2-H0 **-56.0**.

Decision: freeze **COW3_H0** as the provisional physical backbone: 3 cows on `(4,4),(3,4),(4,3)`, main farmer only, no routine HIRE. Hands saved movement but did not increase realized output, so their hire cost was pure drag in this small module.

## H9 — town-conditioned animal demand — PASS

Workflow `34847099631`.

Full-season prior expected town pulls:

- EGG 228;
- MILK 327;
- WOOL 228.

Public shop reveals materially change future product demand. Examples:

- day3 YARN_STORE: expected remaining WOOL 508.5 vs MILK 263.25;
- day3 PIZZA_SHOP: MILK 425.25 vs WOOL 184.5.

Decision: opening COW3 remains justified by prior/runtime evidence, but later capacity should be conditional on observed town shops rather than forced monoculture.

## R2A2-B3 — CARE overlay on COW3/H0 — ACTIVE

Files:

- `candidates/fp001_h8_cow3_care_wrapper.py`
- `tools/fp001_h8_cow3_care_runtime_test.py`
- `.github/workflows/fp001-h8-cow3-care-runtime.yml`

Paired modes on the same fresh seed/seat pairs:

- `NONE`: B2-style COW3/H0 control;
- `SURVIVAL`: CARE only after baseline survival FEED, using otherwise idle turns;
- `DAILY`: use idle turns for extra daily FEED + CARE to bank additional COW production bonus.

Safety invariant: CARE overlay never replaces urgent survival FEED, fertilizer collection or harvest from the B2 scheduler.

### B3 PASS rule

Promote a CARE mode only if it improves paired realized final bank materially on fresh seeds without animal loss or reduction in critical collection/harvest throughput. If CARE fails, retain COW3/H0 unchanged; do not tune indefinitely.

## R2A2-B4 — shop-conditioned expansion — CONDITIONAL NEXT

After B3, test additional capacity selected from current public town shops + expected future demand. Opening COW3 is the fixed control; expansion species is the treatment. No opponent replay information is permitted.

## R2B — common opportunity-cost controller

After the physical production primitive is stable, combine it with H1/H1B using shadow prices for cash, shed space, action/labor, remaining horizon and current public market/town state.

## R3 — adversarial market extensions

Separate experiments: H3 WHEAT input squeeze and H4 premium-sale denial / queue-position response.

## R4 — event-driven inventory MPC

Short-horizon hold/sell/buy/abstain optimization.

## R5 — crop-vs-animal production economics

Compare surviving animal architecture against crop alternatives from first principles under current shops/horizon.

## R6 — full zero-lineage physical scheduler

Expand only after economic modules justify capacity.

## R7 — hierarchical agent

Macro planner + physical scheduler + market MPC.

## Hosted policy

No FP hosted slot yet. Eligibility begins after a complete mechanically valid zero-lineage farm policy clears catastrophe/logistics gates.

## Stop criteria

- Close H1 if cash/shed opportunity cost consumes alpha.
- Close H1B if liquidity/intervention risk consumes timing value.
- Retain COW3/H0 if CARE does not improve it; do not force CARE.
- Cap H8 scale if further expansion adds congestion without return.
