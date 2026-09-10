# CR077B — W/L residual method repair — preregistration

Date frozen: 2026-09-10, before any 2026-09-10 official daily episode dataset is observed by this method.

## Why CR077 is not promotion-valid

CR077 produced a BUY_LAND 96–192 residual signal, but audit found material design defects before the Sep-10 OOT set was available:

1. outcome target was final-money margin rather than the primary competitive W/L objective;
2. state control used only shop count, not exact unlocked-shop identities/multiplicities;
3. legal own private inventory state (`observation.private`: shed, seeds, carried inventories) was omitted;
4. PASS was accidentally searched as a market family although PASS is a farmer/hand action;
5. row bootstrap did not account for episode/team dependence.

Therefore CR077's BUY_LAND result is diagnostic only and may not be promoted or validated directly on Sep-10.

## Frozen CR077B design

### Dates

- Sep-08: fit state-to-outcome and state-to-action controls.
- Sep-09: evaluate the fixed family/window grid and select **at most one** mechanism.
- Sep-10: untouched OOT confirmation of that one frozen mechanism when the official public dataset becomes available.

The Sep-08 controls remain frozen for Sep-10; Sep-09 is not folded into them after selection.

### Primary target

Binary W/L. Tied episodes are excluded. Money margin is not a selection or confirmation target.

### Fixed windows

- 96–192
- 192–360
- 360–540
- 540–719

### Fixed action families / intensity

- HIRE: event count
- BUY_LAND: event count
- BUY_SEED: units
- BUY_ANIMAL: units
- BUY_PRODUCT: units
- SELL: units
- PASS: explicit farmer/hand PASS count

The tested action variable is own-minus-opponent intensity in the window. It is historical analysis only; a later deployed mechanism must use only legal current information.

### State control

Legal current observation only:

- both shared public farms: money, hands, quadrants, hires_today, crop/animal/structure/weed/empty/locked summaries, yield/care/water summaries and compact public position summaries;
- shared market: price and inventory by product;
- shared town: count of each exact unlocked shop plus total;
- **this player's** private observation only: shed quantities, seed counts and carried inventories.

Explicitly forbidden as model features:

- team identity;
- episode id;
- seed;
- opponent private shed/seeds/inventories.

Team and episode identity may be used only for robustness/resampling.

### Residualization

- regularized logistic model: state -> W/L probability;
- regularized ridge model: state -> action-intensity difference;
- selection statistic: correlation between OOT action residual and OOT W/L residual.

### Sep-09 discovery gate

A family/window is eligible only if all are true:

- |residual correlation| >= 0.20;
- action-difference std >= 0.5;
- episode-cluster bootstrap 80% interval excludes zero in the same direction;
- leave-one-team-out sign fraction >= 0.75;
- at least 3 leave-one-team-out evaluations.

Select exactly one eligible mechanism by largest absolute residual correlation. If none qualifies, stop this residual shortlist; do not promote a runner-up.

### Sep-10 fresh OOT gate

For the frozen Sep-09 mechanism only:

- same correlation direction;
- |residual correlation| >= 0.15;
- episode-cluster bootstrap 80% interval excludes zero;
- leave-one-team-out sign fraction >= 0.65;
- at least 3 leave-one-team-out evaluations.

If Sep-10 is unavailable, decision is WAIT and the method/gates must not be altered while waiting.

## Decision tree

- Sep-10 PASS -> build **CR078**, one-mechanism causal counterfactual/ablation. No direct strategy promotion from CR077B.
- Sep-10 FAIL -> close this residual shortlist. Do not choose the second-ranked Sep-09 mechanism post hoc.
- no Sep-09 eligible mechanism -> close shortlist immediately and move to the next independent current-meta/adaptation architecture branch.

No automatic Kaggle submission is authorized by CR077B.
