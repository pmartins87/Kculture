# ALL3 V13C Current Frontier Hard-Context Census — Binding Result — 2026-09-20

Binding completion workflow: **`35523990217`**.

Decision: **`V13C_CURRENT_FRONTIER_HARD_CONTEXTS_READY`**.

## Mechanical completeness

The original V13C workflow `35520875702` completed 72/76 episodes and correctly failed closed on one source-drift event:

- rank 14 unversioned ref: `tetsutani/demand-preserving-turn-sale-timing`;
- frozen V13B main SHA: `1aa3717b3201997a95920c80cf5612c23f78f8716c7b1084b6a345ca4eae7e4f`;
- later unversioned download no longer matched that SHA.

Historical public-version resolution workflow `35523343530` found the exact frozen bytes at:

`tetsutani/demand-preserving-turn-sale-timing/versions/4`

with:
- main SHA `1aa3717b3201997a95920c80cf5612c23f78f8716c7b1084b6a345ca4eae7e4f`;
- archive SHA `24250d6de0e1bf143ea0cc1b2bdab541aa94ee12c09b9f2f6e98e8afb7097610`.

Workflow `35523990217` then:
1. reused the 72 mechanically valid original rows;
2. ran exactly the four missing rank-14 contexts against immutable version 4;
3. verified the full 76-key set `(source SHA, seed, seat)` against the original frozen population;
4. applied the unchanged pre-registered V13C gate.

No strategic context was selected or dropped during the repair.

## Binding census

- completed games: **76/76**;
- hard contexts: **24**;
- unique hard source SHAs: **10**;
- ties: none in the hard set; all 24 were losses.

Hard-source summary:

- rank 1 — 2 losses / 4 games;
- rank 2 — 2/4;
- rank 4 — 2/4;
- rank 6 — 2/4;
- rank 8 — 2/4;
- rank 9 — 2/4;
- rank 11 — 2/4;
- rank 19 — 2/4;
- rank 14 immutable version 4 — **4/4 losses**;
- rank 23 V53 opening signature — **4/4 losses**.

The 24 binding hard contexts are frozen in:

`configs/all3_v14a_hard_contexts.json`.

## Interpretation

The refreshed current public frontier is not locally trivial for ALL3.

There is sufficient multi-source W/L failure coverage to support bounded causal mechanism discovery.

This result does **not** estimate hosted rating or predict leaderboard performance.

The next binding stage is the pre-registered V14A domain upper-bound:
- MARKET;
- PHYSICAL;
- FULL shadow ceiling.

No Kaggle submission is authorized.
