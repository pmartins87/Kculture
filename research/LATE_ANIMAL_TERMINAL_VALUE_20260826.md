# Late-animal terminal value — exact engine result

Date: 2026-08-26

Purpose: freeze the exact official-mechanics facts needed before designing any late stop-investment candidate.

## Source of truth

Official Kaggriculture engine:

- package: `kaggle-environments==1.32.7`;
- upstream commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`;
- file: `kaggle_environments/envs/kaggriculture/kaggriculture.py`.

## End-of-day timing

The interpreter calls `_end_of_day` only when:

```python
if (step + 1) % turns_per_day == 0:
    _end_of_day(state, env, day)
```

with `turns_per_day=24`.

The final executable action is step 718. Therefore:

- step 671 triggers the day-27→28 refresh;
- **step 695 triggers the day-28→29 refresh**;
- steps 696-718 are the final day;
- there is no executable step 719 and therefore **no end-of-day refresh after the final day**;
- terminal reward is assigned from `farm.money` after step 718 processing.

Thus the refresh after step 695 is the final plant/animal production refresh of the match.

## Exact animal refresh order

For every placed animal at end of day:

1. if `fed_today`, `consecutive_unfed` resets to 0; otherwise it increments;
2. if `consecutive_unfed >= 2`, the animal escapes immediately and the pasture/coop remains empty;
3. if the animal survives and its production schedule fires, it receives base production of 1;
4. an existing `pending_care_bonus` is added to that scheduled production **only when `fed_today` is true**;
5. after scheduled production, `cared_today && fed_today` increments `pending_care_bonus` for a **future** production;
6. fertilizer becomes available;
7. `fed_today` and `cared_today` reset.

## Consequence for CARE at steps 672-695

CARE during the final pre-terminal day (steps 672-695) can only create a new `pending_care_bonus` **after** the step-695 scheduled production check.

There is no later end-of-day production refresh before terminal scoring.

Therefore, subject to the frozen engine above:

> **CARE issued during steps 672-695 has zero direct terminal-production value.**

It does not move the actor and consumes no inventory itself, so replacing it with PASS alone should be behaviorally neutral except for the unused bonus state. A useful candidate must **reallocate** that actor action to something that can still become terminal cash (for example an immediately available HARVEST/COLLECT operation) rather than merely delete CARE.

## Consequence for FEED at steps 672-695

FEED is not universally worthless. It consumes one wheat and can still matter at the step-695 refresh because:

- an animal already at `consecutive_unfed == 1` would escape if left unfed again;
- if a scheduled production fires at step 695, feeding allows an **existing** `pending_care_bonus` to be paid;
- escaping before the production check can destroy an animal with collectible state.

However, if all of the following are true at the FEED decision:

- `consecutive_unfed == 0` (one missed day will not cause escape at step 695);
- the step-695 production is not scheduled, **or** there is no realizable extra output from an existing care bonus because bonus is zero/capped;

then FEED has no remaining production benefit in the season while still consuming one wheat. That is a mechanically justified candidate region for selective suppression, subject to shed-capacity/market-interaction testing.

Base production itself does **not** require feeding if the animal survives: the engine adds base 1 on a scheduled production even when unfed; feeding gates only the existing care bonus.

## Final-day actions 696-718

Because no end-of-day refresh follows step 718:

- FEED cannot create another animal production;
- CARE cannot create a payable future bonus;
- maintenance whose only purpose is a later refresh has zero terminal-production value.

Frozen COK/R4B route tapes already issue zero FEED and zero CARE in 696-718, so this is not the remaining differentiator. The live-meta gap is primarily the **672-695 decision**, where COK routes still contain roughly 8-10 CARE and 9-10 FEED actions depending on route.

## Prize-first candidate implications

Do not implement a blanket `no FEED` rule.

The first scientifically defensible late-animal candidate should be narrow and state-aware:

1. preserve all earlier R4B behavior;
2. in 672-695, recognize CARE as terminally nonproductive and test productive same-position substitution where safe;
3. suppress FEED only when the exact observed animal state proves that the wheat cannot buy remaining production value;
4. retain FEED when needed for survival or an uncapped existing pending bonus;
5. evaluate W/L first across diverse development opponents before any fresh validation;
6. keep all 32 held-out seeds sealed.

This mechanics result is independent of the KEXP-018 live-meta correlation. KEXP-019 separately tests whether strong late stop-investment/animal-exit behavior generalizes across recent top-ladder days.
