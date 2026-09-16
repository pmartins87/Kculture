# Prize Solver V0 — competition architecture

## Sole objective

Maximize the probability of reaching the Kaggriculture prize zone. Solver sophistication has no value by itself. Hosted competitive performance is the arbiter.

## Architecture

`visible current state -> opponent belief -> macro candidates -> value/search -> end-to-end adaptive executor -> action`

### 1. End-to-end adaptive executor

No replay tape is used. Farmer, hands and market orders are all derived from the current observation. Physical divergence therefore does not invalidate a downstream script.

The executor supports:
- survival WATER/FEED;
- animal CARE and fertilizer collection;
- harvest and liquidation;
- adaptive HIRE;
- land expansion;
- animal purchase/build/place;
- crop seed purchase/plant/fertilize;
- item pickup/logistics;
- multi-unit task reservation and routing.

### 2. Opponent model

V0 uses only legal public state. It estimates product pressure from visible crops, animals and currently visible unharvested output. This is intentionally conservative. The interface is designed so CR007/CR086-style learned beliefs can replace the priors later without changing the planner.

### 3. Value model

The planner exposes a stable state-feature contract. V0 starts with economic priors; exact-engine trajectories will train a value estimator for future reward margin. The learned model must replace or improve the priors only after held-out validation.

### 4. Receding-horizon plan selection

The solver reassesses strategy at day boundaries. Existing physical commitments become lower bounds, so replanning is monotone rather than destructive. Near terminal it stops scale-up and prioritizes liquidation.

Initial plan family:
- COW_HEAVY
- COW_MELON
- MIXED_HEDGE
- CROP_PRESSURE
- CONSERVE
- TERMINAL

## Development gates

### PS0 — mechanical closure
12 complete exact-engine games against pass/random/starter/self. No ERROR/INVALID/TIMEOUT. This is a mechanics gate, not a competitive proxy.

### PS1 — value learning
Generate exact-engine trajectories across a heterogeneous opponent/policy pool. Fit V(state) to future final reward margin. Validate on held-out seeds/opponents. Reject if it cannot beat a money-difference-only baseline.

### PS2 — macro search
At sampled day-boundary states, branch candidate strategic macros in the exact simulator over a bounded horizon. Use rollout return + learned terminal V to label/select plans. Measure regret against the best tested macro on held-out states.

### PS3 — opponent model uplift
Compare macro/value decisions with and without opponent-belief features. Keep only if held-out rollout regret or win rate improves. CR007/CR086 knowledge is an input candidate, not a mandatory component.

### PS4 — distilled hosted candidate
Freeze solver decisions into a Kaggle-safe package. Run only legality/runtime/sanity checks locally, then submit early to hosted evaluation.

### PS5 — hosted iteration
Hosted score controls continuation. Use daily submission budget deliberately. Local metrics explain and filter; they do not veto mechanically valid candidates indefinitely.

## Binding anti-drift rules

1. Prize probability is the only project objective.
2. No state-changing patch may be grafted onto a replay tape.
3. No multi-stage local validation ladder before every hosted sensor.
4. New techniques enter only if they improve the solver, opponent belief, value estimate, execution, or hosted iteration speed.
5. A user comment does not by itself change architecture.
6. Reuse proven findings (CARE, cow scale, M6S1, town timing, CR086/CR007 signals) as components; do not restart research from zero.
