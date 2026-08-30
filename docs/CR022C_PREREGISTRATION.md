# CR022C — Adaptive sale quantity preregistration

Frozen before any CR022C candidate result.

## Question

CR008 produced the largest hosted gain so far, but every high-confidence adaptive trigger sells the entire available CARROT/STRAWBERRY stock. CR022C tests whether the response **quantity alone** can be improved while holding the forecast, products, thresholds, timing and append placement fixed.

This experiment must not test early queue placement, MELON expansion, new classifiers, opponent identity, route inference, or production changes.

## Frozen arms

- `q100`: exact CR008 behavior, 100% of triggered stock — control.
- `q75`: ceil(0.75 × triggered stock).
- `q50`: ceil(0.50 × triggered stock).
- `q25`: ceil(0.25 × triggered stock).

When CR008 would not trigger, every arm must behave identically. When it triggers with positive stock, the fractional arm sells at least one unit. Market order remains appended exactly where CR008 appends it.

## Frozen data

Seed config: `configs/cr022c_quantity_preregistered_seeds_v1.json`.

- Stage A: 12 fresh seeds.
- Stage B: 12 disjoint fresh seeds.
- Exact nine frozen current-meta opponents from `configs/cr015_current_meta_opponents_v1.json`.
- Both seats.
- 216 paired games per arm per stage.
- All 32/32 held-out seeds remain sealed.

No Stage-A or Stage-B seed may be used to design the quantity arms, thresholds, forecast, products or gate.

## Metrics

For each challenger vs `q100`, compute paired:

- terminal own-money gain;
- terminal relative-money gain (`self - opponent`); 
- W/L score gain (win=1, tie=.5, loss=0);
- favorable and unfavorable W/L conversions;
- positive-relative-gain fraction;
- 10% lower-tail CVaR of paired relative gain (mean of worst ceil(10%) paired relative deltas).

A close-boundary subset of 40 tuples is chosen **only** by smallest absolute `q100` terminal relative delta. Challenger results may not influence close-set selection.

## Stage-A eligibility

A non-control arm is eligible only if all are true:

1. zero mechanical errors and all expected pairs complete;
2. broad unfavorable W/L conversions <= favorable conversions;
3. close-subset unfavorable conversions <= favorable conversions;
4. broad mean W/L score gain >= 0;
5. at least one genuine positive signal exists: either broad net favorable flips > 0, close net favorable flips > 0, or broad mean relative-money gain > 0.

If no arm is eligible, CR022C closes with no Stage B.

## Frozen Stage-A selection

At most one arm advances. Among eligible arms, select lexicographically by the following tuple, largest first:

1. broad `(favorable - unfavorable)` W/L conversions;
2. close `(favorable - unfavorable)` W/L conversions;
3. broad mean W/L score gain;
4. close mean W/L score gain;
5. broad mean relative-money gain;
6. broad 10% lower-tail CVaR of paired relative gain.

This ordering intentionally prioritizes outcomes over money and tail quality over post-hoc storytelling. There is no threshold rescue or second-place substitution after seeing Stage A.

## Stage B confirmation

Only the unchanged Stage-A winner may run Stage B. Its fraction and code are frozen.

Stage B is confirmatory. Promotion beyond CR022C requires:

- zero errors and all pairs complete;
- broad and close unfavorable W/L conversions <= favorable conversions in Stage B;
- Stage-B broad mean W/L score gain >= 0;
- combined Stage A+B broad net W/L conversions >= 0;
- combined Stage A+B broad mean relative-money gain > 0.

Failure closes the quantity branch; the same Stage-A seeds may not be reused to choose a new fraction.

## Interpretation rule

A smaller quantity is interesting only if it improves actual paired game outcomes or preserves outcomes while improving robust relative value. Immediate transaction revenue, top-agent imitation, AUC, or isolated examples cannot promote an arm.
