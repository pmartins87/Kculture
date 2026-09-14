# FP001 E1 — marginal STRAWBERRY result — 2026-09-14

Workflow: `34860319522`

## Question

Can one early STRAWBERRY add value to the proven B4 animal controls **without displacing any non-PASS animal action**, using only otherwise-idle main-farmer turns and reserving at most two fertilizer units for the H11 schedule?

This was deliberately a narrow causal gate. It does **not** test whether STRAWBERRY is globally bad or whether elite mixed-crop farms are bad. It tests only the residual-idle-turn architecture.

## Mechanical result

All treatments completed with full cow survival. The gate is mechanically valid.

### COW4_DAILY

- control mean delta: `+38,344.0`;
- S1 hybrid mean delta: `+38,661.0`;
- paired S1-control: `+317.0` mean, median `-2,474.0`, range `[-3,538, +9,754]`, **2W-6L**;
- hybrid crop: 8/8 planted, only 8 WATER actions total, zero fertilizer, zero harvest, zero berries sold;
- crop failed in all 8 episodes.

Interpretation: the positive mean is not credible crop value; it is dominated by variance while the treatment itself produced no realized STRAWBERRY output. COW4_DAILY does not provide enough contiguous residual labor for this crop architecture.

### COW5_SURVIVAL

- control mean delta: `+39,317.0`;
- S1 hybrid mean delta: `+38,623.5`;
- paired S1-control: **`-693.5` mean**, median `-648.5`, range `[-3,809, +2,332]`, **4W-4L**;
- hybrid crop: 8/8 planted, 72 WATER, zero fertilizer, 32 HARVEST actions, **32 berries sold total = 4/episode**;
- animal output/survival remained intact.

Interpretation: this backbone has real idle capacity and can realize an unfertilized crop, but the residual main-farmer overlay still cannot execute the H11 fertilizer schedule and does not beat the animal-only control.

### COW5_DAILY

- control mean delta: `+43,340.75`;
- S1 hybrid mean delta: `+43,240.75`;
- paired S1-control: **exactly `-100` in 8/8**;
- control main-farmer idle PASS count: zero;
- hybrid never planted, watered, fertilized or harvested a crop.

Interpretation: COW5_DAILY is action-saturated. The treatment only paid the 100 seed cost and never obtained a physical turn to plant it.

## Decision

**Close only the residual-idle-main-farmer STRAWBERRY architecture. Do not close STRAWBERRY.**

The result identifies labor allocation as the bottleneck:

- H11 independently proves positive fertilizer-to-STRAWBERRY conversion economics;
- CR087 elite macro evidence independently shows premium crops are common in ~3000-class production programs;
- E1 shows those economics cannot be unlocked by simply appending crop tasks after the animal scheduler has consumed its preferred actions.

Therefore the next causal gate is E2: preserve the main farmer's animal policy and assign crop work to a bounded dedicated hand. HIRE must be evaluated in this new workload context rather than extrapolating the earlier animal-only negative-HIRE result.

## What would change this decision

The residual architecture can be reconsidered only if a later scheduler redesign creates documented contiguous main-farmer capacity without sacrificing more valuable animal actions. Threshold tuning inside the current E1 wrapper is not authorized.
