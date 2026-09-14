# FP001 E2 — dedicated STRAWBERRY hand protocol — 2026-09-14

## Objective

Test whether cheap bounded labor unlocks the positive H11 STRAWBERRY/fertilizer mechanism **without stealing physical actions from the proven B4 animal backbone**.

This is a causal labor-revaluation gate, not a final elite policy.

## Fixed treatment

- one early STRAWBERRY at `(4,3)`;
- animal main-farmer policy remains the existing H10/B4 scheduler;
- crop physical work is assigned only to the first current farm hand;
- at most one HIRE is requested per day;
- the first daily HIRE is the official Fibonacci first hire and costs `farmHandCostMult * 1`; default `farmHandCostMult=1`;
- hands are rehired only while opening setup or productive crop work remains;
- no late replant after the opening day 0/1 treatment;
- crop hand handles PLANT, WATER, H11 FERTILIZE ages 9/13 and HARVEST;
- animal-generated fertilizer is reserved from shed only to satisfy remaining H11 needs; excess fertilizer remains saleable;
- STRAWBERRY realized in shed is sold without introducing a new timing overlay;
- no CR086/CR088 market operator is added in E2. Market integration remains a later factorial layer.

## Matched architectures

For each animal backbone:

1. animal-only control `S0H0`;
2. E1 one-STRAWBERRY/no-hand `S1H0`;
3. E2 one-STRAWBERRY/dedicated-hand `S1H1`.

Backbones:

- COW4_DAILY;
- COW5_SURVIVAL;
- COW5_DAILY.

Thus E2 identifies both:

- `S1H1 - S1H0`: marginal value of labor in a real crop workload;
- `S1H1 - S0H0`: total value of the labor-enabled crop module versus the animal-only control.

## Frozen evaluation

- exact `kaggle-environments==1.32.7` through repository requirements;
- 4 fresh seeds × both seats = 8 paired observations per architecture;
- same pass opponent used by E1 so this remains a production/economics causal gate, not a population-strength claim;
- require DONE/DONE and full expected cow survival.

Record:

- final-bank delta and paired W/T/L;
- cow survival;
- HIRE count;
- main-farmer FEED/CARE/movement;
- hand productive actions and movement;
- crop planted/failed;
- WATER/FERTILIZE/HARVEST counts;
- berries sold;
- milk and fertilizer sold;
- fertilizer retained/consumed indirectly through action counts.

## Promotion rule

E2 labor is promoted only if `S1H1` produces a positive paired realized-value delta versus both its `S1H0` crop control and its `S0H0` animal control without animal catastrophe.

A small positive result may justify scale testing, but not hosted submission. A non-positive labor delta closes this particular dedicated-one-hand/one-STRAWBERRY architecture and sends the integration search to lower-labor premium crops / mixed macro allocation rather than indefinite HIRE tuning.

## Relation to accumulated competitive knowledge

Failure does not close premium crops: CR087 shows top policies use coherent mixed production rather than residual appendages. Success does not prove prize-class strength: survivors still require elite-informed mixed production, heterogeneous population testing and hosted calibration.
