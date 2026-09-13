# CR084 — temporal high-strength population proxy protocol

Status: **FROZEN BEFORE QUERYING THE HOLDOUT WINDOW / NO HOSTED SUBMISSION AUTHORITY**

## Purpose

CR083 proved that local dominance over our historical anchor panel is not sufficient evidence of live-population transfer. CR084 therefore requires a separate population-strength stress layer after any local promotion PASS.

The 36 hosted CR083 episodes used to discover the late-livestock failure are spent exploratory evidence and are explicitly excluded from this proxy.

## Temporal holdout freeze

CR084's architecture protocol was committed at **2026-09-13T08:00:30Z** in commit `49f8e4c6a7f166aa041570ea0d91a528f7e726aa`.

The holdout window is frozen without inspecting its episode outcomes:

- include CR083 submission `56199767` PUBLIC completed episodes with `createTime >= 2026-09-13T08:00:31Z`;
- include only episodes with `createTime <= 2026-09-13T12:55:00Z`;
- exclude validation episodes;
- exclude every episode in the original 36-replay discovery freeze;
- do not extend the window after seeing results.

The upper bound predates this protocol file and the CR084 promotion result. It is fixed to prevent result-dependent sample growth.

## Opponent-strength classification

After this protocol is committed, take one authenticated full Kaggle leaderboard snapshot. Match opponents by exact public team name.

High-strength episode = opponent score **>= 2300** in that single frozen snapshot.

The `2300` boundary was already defined before CR084 as the approximate top-1000 population threshold; it is not selected from this holdout.

If fewer than **4** holdout episodes have matched opponents at `>=2300`, the proxy is **INCONCLUSIVE / NO HOSTED AUTHORIZATION**, not PASS.

## Replay reproduction firewall

For every selected high-strength holdout episode:

1. load the exact public replay;
2. feed the CR083 seat's legal observation sequence to the exact frozen CR083 package SHA `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`;
3. account for Kaggle replay storage convention in which the action generated from observation `t` is stored in replay step `t+1`;
4. require **100% exact action reproduction** for all comparable steps.

Any reproduction mismatch invalidates that episode for causal interpretation. If any selected high-strength episode fails reproduction, the proxy as a whole is invalid/inconclusive until the parser/runtime discrepancy is resolved; no score interpretation.

## CR084 semantic replay check

Run exact frozen CR084 SHA `3aa08bb2ee163d1707dbf0bf9d2cb4b6f8c194fa2dbd715c38a67a4a41d414a2` on the same legal observation sequences.

Every CR084-vs-CR083 difference must satisfy the frozen architecture:

- `576 <= step < 696`;
- same market queue;
- only an engine-noop physical action becomes `FEED`;
- unit is on a live animal;
- `fed_today == False`;
- `consecutive_unfed >= 1`;
- unit carries at least one WHEAT;
- no identity, EpisodeId, rating, hidden seed, future state, or opponent-private input is passed into the agent.

Identity/rating/episode metadata may be used only by this offline evaluator to select and label holdout episodes; it is never a runtime feature.

## Confirmed-preventable-escape metric

To avoid treating every static replay trigger as causal value, deduplicate candidate triggers by `(episode, day, animal tile)` and keep only the first CR084 rescue opportunity for that animal/day.

A first rescue opportunity is counted as a **confirmed preventable escape** only when the baseline CR083 replay shows that same live animal disappearing at the next day boundary after remaining unfed under the baseline trajectory. Under the already-audited Kaggriculture mechanic (two missed feeds -> escape), a successful CR084 FEED at the frozen opportunity prevents that specific imminent starvation escape for that boundary.

This is a mechanism-alignment proxy, not a simulated live rating and not permission to use future information at runtime.

## Frozen PASS criteria

The temporal high-strength proxy PASS requires **all**:

1. at least 4 matched high-strength holdout episodes;
2. 100% exact CR083 replay-action reproduction on every selected episode;
3. 100% CR084 semantic-difference fidelity to the frozen intervention;
4. at least **2 distinct high-strength episodes** contain one or more confirmed preventable escapes addressed by CR084;
5. total confirmed preventable escapes across the high-strength holdout is at least the number of selected high-strength episodes (mean >= 1 per episode);
6. among high-strength holdout episodes that CR083 lost, at least **50%** contain one or more confirmed preventable escapes addressed by CR084;
7. no execution/parser/runtime error.

If there are zero high-strength losses, criterion 6 is vacuously satisfied but criteria 4–5 still apply.

## Decisions

- Data insufficient or replay reproduction invalid: `CR084_PROXY_INCONCLUSIVE_NO_HOSTED_ACTION`.
- Any substantive PASS criterion fails: `CLOSE_CR084_CRITICAL_FEED_RESCUE`.
- All criteria pass **and** the separately frozen local promotion gate passes: `CR084_ELIGIBLE_FOR_SLOT_ACCOUNTING_AND_ONE_HOSTED_PROBE_REVIEW`.

Even the final eligibility decision does not itself submit anything. Slot accounting and a final current-state check remain required.
