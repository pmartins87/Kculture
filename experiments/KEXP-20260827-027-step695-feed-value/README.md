# KEXP-20260827-027 — exact step-695 FEED value audit

Status: **RUNNING / DIAGNOSTIC ONLY**

## Prize-first question

KEXP-024 proved that reallocating terminally useless CARE is safe but insufficient: the candidate tied the frozen R4B modern panel at 81-15.

The next animal hypothesis targets an actual scarce resource: WHEAT consumed by FEED. A blanket late FEED suppression is unsafe because feeding can prevent animal escape and can unlock a realizable pending CARE bonus on the final production refresh.

This audit therefore starts at the narrowest exact-mechanics boundary: **step 695**, the final executable action before the last animal production refresh. There is no later same-day unit action after this step, so retaining a wheat here cannot block a later pickup or harvest before inventories are dropped to the shed.

## Frozen protocol

Run unchanged `R4B-market-only-validated-v1` against deterministic `starter` on:

- all 16 development seeds;
- all 20 exploratory live-meta environmental seeds.

At every base FEED intent on step 695, inspect the acting animal tile and current inventory state.

A FEED is counted as mechanically removable only when all are true:

1. `consecutive_unfed == 0`, so skipping this feed cannot cause escape at the step-695 refresh;
2. feeding unlocks **zero realizable incremental pending-care production** after the animal `max_held` cap is applied;
3. the acting unit actually holds WHEAT;
4. current shed + carried inventories including the retained wheat fit within the official shed capacity, so the saved unit survives the immediately following end-of-day drop.

No action is changed by this experiment.

## Gate

This experiment does not promote a policy by itself.

A dedicated step-695 FEED-suppression candidate is worth building only if mechanically removable FEED occurs in at least **25% of episodes in both development and exploratory-live-meta pools**. Below that frequency, the exact one-step rule has too little prize-relevant ceiling and the animal branch should move to a broader but still state-aware late-FEED planner.

No validation or held-out seeds are accessed. No seed, episode or opponent identity may be used in a later policy.

Tool: `tools/audit_step695_feed_value.py`
Frozen tool blob: `cbd58411823bdc8628a9fea40ae2d6d7e36b6277`
