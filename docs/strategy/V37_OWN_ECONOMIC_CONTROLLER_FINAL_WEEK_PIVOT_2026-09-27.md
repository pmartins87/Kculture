# V37 — Own Economic Controller / Final-Week Pivot — 2026-09-27

## Why this pivot exists

The V35 exact-public-agent transfer failed severely on our hosted ladder:
- Barnyard V7 56593614: 740.4
- Kaito V2 56593613: 809.9

V36A then prepared Ahmed/Tetsutani/Rayk as current public probes. That was useful as a diagnostic exercise, but it must **not** become the project strategy.

Inspection of the exact V30B source shows that even our recent strongest reproducible baseline is itself heavily descended from public lineages (Ahmed Berat Ozer, yhay81, tetsutani, prvsiyan, etc.). Continuing to remix whole public policies does not solve the transfer problem.

## Binding strategic change

**Do not submit Ahmed V45, Tetsutani V23 or Rayk V22 merely because their public ratings are high.**

They are now:
1. opponent/reference policies;
2. mechanism sources for analysis;
3. current-meta probes;
4. regression tests.

The next intended Kaggle candidate is **V37: an own economic controller**.

## V37 design

Keep only battle-tested mechanical chassis pieces when necessary for engine correctness (state parsing, action serialization, route execution, reset/seat safety). Replace strategic selection with our own observation-driven controller.

### 1. Economic state model
At each decision point estimate:
- current market inventory and marginal price by product;
- remaining town demand;
- remaining horizon;
- shed occupancy/capacity (100);
- cash and committed capital;
- labour/hands cost;
- crop/animal production pipeline already owned;
- opponent public production pressure.

### 2. Marginal portfolio allocator
Choose additional crop/animal capacity from estimated remaining net present value:
expected sale value after own/opponent supply + town demand
minus seed/animal/land/feed cost
minus marginal labour/actions
minus shed congestion/opportunity cost.

No fixed farm composition is sacred.

### 3. Labour controller
Select hires from marginal value of executable work versus Fibonacci hire cost.
A hand is purchased only when there is enough high-value executable work to repay it.

### 4. Market controller
Sell by marginal post-sale price and expected future demand, not fixed tape timing.
Protect premium products from dumping into their own nonlinear price collapse.
Use controlled price pressure against the shared book only when expected opponent damage exceeds our foregone revenue.

### 5. Storage/cash constraints
Treat shed capacity and short-term cash as hard constraints, not soft heuristics.
Prevent asset purchases that cannot be serviced or monetized.

### 6. Terminal controller
Near the end:
- stop capital expenditure that cannot amortize;
- maximize realizable bank;
- liquidate inventory/cargo with explicit remaining-turn feasibility;
- do not preserve theoretical terminal value that cannot become cash.

## Validation policy

Public agents are opponents, not submissions.
Primary validation:
1. mechanics/smoke;
2. paired-seat matches against a current heterogeneous panel including V30B, Ahmed V45, Tetsutani V23, Rayk V22 and other fresh meta references;
3. mechanism-level diagnostics (bank decomposition, product revenue, labour cost, unused actions, shed overflow, stranded capital);
4. then hosted ladder as the only final authority.

Do not require a huge offline win-rate gate: local-to-hosted correlation has already proven weak. Offline testing is for eliminating obvious regressions and identifying causal failure, not certifying leaderboard strength.

## Submission budget

Three UTC-day submissions remain from the previously verified 2/5 state.

Do not spend them simultaneously.
Do not preserve Barnyard/Kaito.
Use them sequentially on materially different V37 hypotheses so each hosted result informs the next.

First shot should be an own V37 candidate, not Ahmed/Tetsutani/Rayk, unless a later explicit evidence result proves a public control is uniquely informative.

## Immediate task

Build the smallest viable V37 around a known mechanically reliable chassis, with our own strategy/economics layer, and get one causal candidate ready for hosted calibration today.
