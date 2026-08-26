# Exact Kaito V27 static audit — 2026-08-26

## Artifact

Exact public Version-4 `main.py` acquired through KaggleHub and verified at SHA-256:
`f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`

See `research/provenance/kaito_v27_v4.json`.

## Runtime architecture

The policy contains one compressed **719-step action tape** used in both seats. Runtime adaptation is intentionally narrow:

1. actor-local weed repair for planned `BUILD_PASTURE` / `PLANT` actions;
2. alignment of hand-action count to observed active hands;
3. dynamic reordering of already-existing `SELL` slots using official price-impact mechanics;
4. bounded Town-demand weighting in the rebalance regime;
5. safe PASS fallback on exceptions.

Opponent identity is not used.

## Opening

Step 0 market plan:

- 4 × `HIRE`;
- buy 1 COW;
- buy 4 SHEEP;
- buy 5 WHEAT seeds;
- buy 5 MELON seeds;
- buy 5 WHEAT product.

The physical route immediately builds/places the first cow and four sheep while planting melon/wheat.

This is materially different from Kculture's COK-derived opening and matches the notebook's reported high-meta HIRE4 / 1C-4S prior.

## Expansion milestones

Exact planned animal purchases:

- step 0: +1 cow, +4 sheep;
- step 120: +1 cow;
- step 161: +2 cows;
- step 168: +2 cows;
- step 192: +2 cows;
- step 361: +1 cow.

Total planned purchases: **9 cows + 4 sheep**.

Land purchases:

- step 160: first `BUY_LAND`;
- step 240: second `BUY_LAND`.

The major continuation reset therefore coincides directly with the first land expansion and a rapid cow expansion around steps 160–192.

## Aggregate planned market quantities

Purchases across the 719-step tape:

- COW: 9;
- SHEEP: 4;
- WHEAT seeds: 148;
- MELON seeds: 19;
- STRAWBERRY seeds: 37;
- WHEAT product: 212.

Planned sales:

- FERTILIZER: **235**;
- WHEAT: **455**;
- WOOL: **132**;
- MILK: **241**;
- MELON: **114**;
- STRAWBERRY: **286**.

There are 168 route-existing SELL orders. Runtime market logic can reorder those existing SELL slots but does not create new ordinary sale slots.

## Physical action profile

Across farmer + hand action slots, the route is strongly labor-intensive. Static action counts include:

- WATER: 1,010;
- movement: NORTH 838, WEST 811, EAST 634, SOUTH 553;
- HARVEST: 390;
- COLLECT_FERTILIZER: 296;
- FEED: 290;
- CARE: 285;
- PLANT: 199;
- PICKUP: 135;
- FERTILIZE: 72;
- DROP: 57;
- DIG: 40;
- BUILD_PASTURE: 13;
- PLACE: 13.

The action tape also contains 262 `HIRE` market orders over the season, reflecting repeated labor refresh/scale rather than only the Day-0 HIRE4 opening.

## Terminal behavior

The route remains physically active through the end:

- steps 713–717 contain multiple harvest/drop operations and product sales;
- step 718 contains one hand `DROP` and only one planned market order: `SELL WHEAT 7`.

This makes terminal sale completeness a mechanically plausible future ablation on top of V27, because final reward is cash only and market processing follows unit actions. It must still be tested experimentally: the planned final route may already be balanced around exact carried/shed quantities and sale-order price impact.

## Strategic implication for Kculture

If `KEXP-011` shows V27 dominates R4A/R4B, the clean next research hierarchy is:

1. freeze exact V27 as a **new public engineering base**, not yet a Kculture champion;
2. first test a minimal terminal sale-completeness overlay on V27;
3. separately study the step-160–240 continuation (first land expansion, cow scaling, labor pattern and market cadence);
4. avoid mixing opening, midgame and terminal changes in one experiment;
5. require direct same-seed comparison against exact V27 before promotion;
6. only open validation for a frozen improved candidate, never for exploratory variants.

If V27 does not dominate locally, retain it as an independent high-rating adversary and diagnose the matchup instead of copying its architecture.
