# FP001 E2B — no-weed causal result — 2026-09-14

Workflow **`34865508451`**, job `104048214995`, SUCCESS.

## Purpose

E2B reran the exact frozen E2 candidate with `weedSpawnChance=0` for every treatment/control in order to remove the action-dependent weed RNG discovered after E2. Six fresh seeds (`69301..69306`) × both seats were used for each architecture. With a pass opponent the two seats are symmetric, so seat duplication is a mechanics check rather than independent environmental variation.

## Mechanical result

Every architecture preserved all expected cows.

Every `S1H1` dedicated-hand treatment achieved the intended crop mechanics across all 12 seat-runs:

- crop established 12/12;
- zero pre-productive crop deaths;
- crop harvested 12/12;
- 204 HIRE orders total = 17/episode;
- 204 WATER = 17/episode;
- 24 FERTILIZE = 2/episode;
- 48 crop HARVEST = 4/episode;
- 96 STRAWBERRY sold = **8/episode**;
- main-farmer FEED/CARE/movement totals and MILK output totals match the corresponding animal backbone aggregates;
- hand PASS = 3972 total = ~331/episode, confirming severe under-utilization of one hand for one plant.

## Direct labor value versus the same crop/no-hand state

### COW4_DAILY
`S1H1 − S1H0`:
- mean **+1438.17**;
- median +1466;
- range +1298 to +1520;
- **12W-0L**.

### COW5_SURVIVAL
`S1H1 − S1H0`:
- mean **+643.5**;
- median +646.5;
- range +554 to +708;
- **12W-0L**.

These are stable and of economically plausible scale.

### COW5_DAILY
`S1H1 − S1H0`:
- mean −3335.5, median +2060;
- 8W-4L;
- four losses are the duplicated-seat realizations of seeds 69305/69306, with large negative deltas.

Because `S1H0 − S0H0` is exactly −100 in all 12 COW5_DAILY runs, the nonlinear loss is introduced by the actual labor-enabled crop module, not by seed purchase alone.

## Total module versus animal-only control

### COW4_DAILY
`S1H1 − S0H0`:
- mean +2068.17;
- median +2266.5;
- 8W-4L;
- range −3830 to +8697.

However `S1H0 − S0H0` itself remains highly variable (mean +630, 6W-6L, range −5342 to +7277) because the no-hand E1 overlay physically moves the main farmer when it finds residual PASS. It is therefore not a clean neutral bridge to the animal-only control.

### COW5_SURVIVAL
`S1H1 − S0H0`:
- mean −2218.17;
- median +1820;
- 8W-4L;
- range −16242 to +4313.

Again the inherited E1 no-hand overlay already perturbs the main-farmer route (`S1H0 − S0H0` mean −2861.67, 8W-4L, range −16950 to +3621). This prevents interpreting the total-module result as a simple crop cashflow estimate.

### COW5_DAILY
`S1H1 − S0H0`:
- mean −3435.5;
- median +1960;
- 8W-4L;
- range −21405 to +5432.

Here the interpretation is sharper because `S1H0 − S0H0 = −100` exactly in 12/12. The dedicated-hand crop module is positive in seeds 69301–69304 but catastrophically negative in 69305/69306.

## Interpretation

E2B proves two facts but does **not** yet justify promotion:

1. dedicated labor can execute the H11 crop mechanism cleanly without directly stealing main-farmer actions;
2. small financial/inventory changes can trigger large downstream nonlinear effects in the animal backbone, especially COW5_DAILY.

The second effect remains unexplained and must be treated as potentially real until diagnosed. It is not acceptable to average it away: a prize-class controller must understand and avoid such liquidity/timing cliffs.

The nominal cashflow scale provides a sanity bound: STRAWBERRY base price 120, fertilizer base 100, seed cost 100 and ~17 first-hire costs of 1. Eight berries in exchange for two retained fertilizer units should create a direct value on the order of hundreds, not ±10k–20k. Therefore those large deltas imply an indirect state transition in the backbone.

## Decision — E2C required before E3

Do not promote or close E2 on aggregate E2B means yet.

Focused diagnostic **E2C** is authorized on COW5_DAILY seeds 69304 (positive control), 69305 and 69306 (catastrophic), comparing animal-only versus exact frozen E2 with weeds disabled. It must locate the first divergence in:

- cash / affordability;
- WHEAT purchases and inventory;
- animal setup timing;
- main-farmer actions;
- care/feed alignment and `pending_care_bonus`;
- MILK sales/timing.

Candidate parameters remain frozen during diagnosis.

## Gate after E2C

- If catastrophic seeds are explained by a correctable scheduler interaction (for example a liquidity threshold that causes missed fed-production days), fix that mechanism with an explicit matched ablation before scaling crops.
- If the loss is intrinsic to the added crop economics on COW5_DAILY, close that backbone for crop integration and retain only architectures with robust total value.
- Only after the cliff is explained may the project test multiple crops per existing hand / MELON comparison.
