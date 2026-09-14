# FP001 ROADMAP — first-principles economy

Updated: 2026-09-14

Objective: produce a hosted-competitive zero-lineage Kaggriculture agent by deriving policy from official mechanics and runtime state rather than competitor replay imitation.

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

Workflow `34844070131`.

## R2A2-A — exact FEED/CARE frontier — PASS

Workflow `34844616747`. Abstract control favored SHEEP but did not settle physical runtime architecture.

## R2A2-B1 — one-animal runtime — PASS

Workflow `34844919444`: COW +4721 mean, SHEEP +3593, GOOSE +3457.

## R2A2-B2 — multi-animal runtime — PASS

Workflow `34846686427`.

Mean deltas:

- COW3_H0 +12880.75;
- COW3_H2 +12824.75;
- COW2_SHEEP1_H2 +11881;
- COW1_SHEEP2_H2 +10874.75;
- SHEEP3_H2 +9807;
- COW2_H0 +8522.25;
- COW2_H2 +8465.

Routine HIRE was negative marginal value: COW2 -57.25 and COW3 -56.0 for H2-H0.

## H9 — town-conditioned animal demand — PASS

Workflow `34847099631`. Prior expected full-season animal-product pulls: EGG228, MILK327, WOOL228. Public shop composition materially changes remaining demand, so later expansion should be shop-conditioned.

## R2A2-B3 — COW3 CARE overlay — STRONG PASS

Workflow **`34847600991`**. Initial run `34847381440` failed before simulation due import-path infrastructure only; rerun used unchanged policy and passed.

Paired 16 fresh seed/seat cases:

- NONE mean +13101.375;
- SURVIVAL CARE mean +22103.5;
- DAILY FEED+CARE mean **+27308.5**.

Paired gains:

- SURVIVAL-NONE **+9002.125 mean**, 16/16 wins;
- DAILY-NONE **+14207.125 mean**, 16/16 wins;
- DAILY-SURVIVAL **+5205 mean**, 16/16 wins.

Decision: CARE is promoted. Current provisional production backbone is **COW3 + main farmer only + DAILY FEED/CARE**, with urgent survival/collection/harvest safety retained.

## H10 — compact COW scale + batch harvest — ACTIVE

Workflow **`34848106237`**.

Motivation:

- B2 COW3 harvested roughly one action per MILK despite COW `max_held=6`;
- COW3_H0 exceeded COW2_H0 by ~+4358.5 mean, so scale had not saturated at 3;
- B2 COW3 main farmer still had substantial unused turn budget.

H10 test ladder:

1. B2_COW3 control;
2. H10_COW3 threshold1 — measures new compact scheduler/layout vs B2;
3. H10_COW3 threshold6 — isolates batching within H10;
4. H10_COW4 threshold6;
5. H10_COW5 threshold6;
6. H10_COW6 threshold6.

Compact zero-lineage layout: `(4,4),(3,4),(2,4),(1,4),(1,3),(2,3)`. Main farmer only. Bulk setup pickup, urgent survival FEED, daily fertilizer collection, MILK hold to threshold where safe.

### H10 gate

- Promote batching only if paired T6 > T1 without survival loss.
- Increase scale only while marginal realized bank stays positive and full survival is stable.
- Treat animal loss as scale-saturation evidence, not as a reason to hide/abort the result.
- Do not add hired hands until a scale level demonstrates congestion that hands can profitably relieve.

## R2A2-B4 — combine winning H10 scale with DAILY CARE — CONDITIONAL NEXT

Once H10 identifies the best stable no-CARE scale, apply the already-proven DAILY CARE mechanism to that scale. Compare against both the H10 no-CARE control and the current COW3 DAILY backbone.

PASS requires paired realized improvement without survival or throughput collapse.

## R2A2-B5 — shop-conditioned expansion — CONDITIONAL

Only after physical scale + CARE stabilizes. Use legal public town shops and expected future demand to choose marginal species/capacity. Opening policy remains mechanics-derived; no replay routes.

## R2B — common opportunity-cost controller

Combine stable production with H1/H1B under cash, shed, action/labor, horizon, market and town-state shadow prices.

## R3 — adversarial market extensions

H3 WHEAT input squeeze and H4 premium-sale denial / queue-position response as separate causal experiments.

## R4 — event-driven inventory MPC

Short-horizon hold/sell/buy/abstain optimization.

## R5 — crop-vs-animal production economics

Compare surviving animal architecture against crop alternatives from first principles under current shops/horizon.

## R6 — full zero-lineage physical scheduler

Expand only after economic modules justify capacity.

## R7 — hierarchical agent

Macro planner + physical scheduler + market MPC.

## Hosted policy

No FP hosted slot yet. Eligibility begins after a complete mechanically valid zero-lineage policy clears the remaining scale/integration gates.

## Stop criteria

- Close H1 if cash/shed opportunity cost consumes alpha.
- Close H1B if liquidity/intervention risk consumes timing value.
- Cap COW scale where marginal realized value becomes non-positive or survival becomes unstable.
- Do not force hired labor if it remains negative marginal value.
