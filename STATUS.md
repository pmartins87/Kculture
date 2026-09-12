# STATUS — Kculture live source of truth

Updated: 2026-09-11 local / 2026-09-12 UTC boundary

Authoritative working branch: `fix/kaggle-parity-v1`. Historical detail remains available in Git history; this file intentionally contains only the current operational state.

## Mission

Maximize the probability of a prize-winning / top-10 Kaggriculture result. Final deadline remains 2026-09-30 23:59 UTC. Do not spend a hosted submission on a candidate that has not passed its frozen gate.

## Incumbents / hosted reality

- CR071M — submission `56124705`; current authenticated API checkpoint: rating **1731.8**, 297 listed episodes. Newest 32 replays: 8W / 22L / 2T, score rate 0.28125. It remains the incumbent reference, not an architecture worth microtuning.
- CR070A — submission `56091951`; current authenticated rating **1724.0**. Newest 32: 8W / 19L / 5T, score rate 0.328125.
- Submission allowance at the latest API checkpoint: 5 currently allowed. This is capacity, not a quota.
- Do **not** submit CR080.

## Closed candidates

- CR078 mirror breaker: closed / FAIL.
- CR079 SpaTaro simple 1-NN behavioral clone: closed / FAIL. Run `34562284953`; composite 0.28566 vs clock 0.37223, worse in 51/51 holdout episodes. No threshold retuning.
- CR080 Mengfei route bridge: **closed / FAIL**. Independent exact confirmation run `34655496708`:
  - vs CR071M: 33–31 = 0.515625, below required 0.5625;
  - vs CR053: 34–30 = 0.53125 vs CR071M 0.59375, delta -0.0625;
  - vs CR061: 33–31 = 0.515625 vs CR071M 1.0000, delta -0.484375;
  - vs CR065: 39–25 = 0.609375 vs CR071M 0.890625, delta -0.28125;
  - zero execution failures; frozen gate decision `CLOSE_CR080_NO_RETUNING`.
  No CR080A/B/C rescue is permitted.

## Active diagnostics

Run `34668446703` — CR080 post-failure closed-loop diagnostic — is currently running on the already-used confirmation seeds for explanation only. Frozen hypotheses: labor-plan/hand-count drift, position-repair cascade, route-stitching economic drift, or strategic failure if those mechanical effects are weak. It cannot reopen CR080. Protocol: `docs/strategy/CR080_FAILURE_DIAGNOSIS_PROTOCOL_2026-09-11.md`.

## Current frontier — authenticated API snapshot

Fresh read-only run `34668645531` walked the top 20 and sampled 80 current hosted replays. Current leaders in that snapshot:

1. Majkel1337 — **3181.9** — submission `56156662`;
2. ymg_aq — **3075.1** — submission `56161578`;
3. Unknown Mother-Goose — **3056.5** — submission `56169353`;
4. Artem The Farmer — **3029.3**;
5. SpaTaro — **3029.0**.

The key structural discovery is that a recent hosted loss-family faced by CR071M (Sidharth Hulyalkar / XiaoYan12 / ocean240812) is closely related to current #3 Unknown Mother-Goose. Against the frozen loss-family reference over steps 0–191, the four sampled current UMG replays average about 90% exact farmer-action similarity, 74.5% hands similarity and 78.8% market similarity. The three hosted family members beat CR071M by roughly 4k–9.6k reward and show large market/economy changes beginning immediately while retaining much of the familiar physical backbone.

This makes current UMG, rather than historical Mengfei or simple SpaTaro replay imitation, the preferred bridge target.

## Active research — CR081

CR081 is a **current ~3056-lineage market/economy bridge**, frozen before deep-corpus inspection. Protocol: `docs/strategy/CR081_CURRENT_3056_BRIDGE_PROTOCOL_2026-09-11.md`.

Run `34669006417` is collecting through the authenticated official Kaggle API:

- newest 128 episodes of UMG `56169353` — primary target;
- newest 64 episodes of Majkel `56156662` — #1 context;
- newest 64 episodes of ymg_aq `56161578` — #2 context.

CR081 Gate A asks whether UMG preserves enough of the known physical lineage while exposing a reproducible market/economic transformation. If it passes, build exactly one market-first/state-legal bridge and freeze its exact H2H promotion gate before results. If it fails, do not create threshold variants; move to a state-adaptive macro-economic policy trained on the current frontier.

## Operational policies that remain binding

- Authenticated Kaggle API first; screenshots/UI only as fallback. See `docs/strategy/KAGGLE_API_FIRST_POLICY.md`.
- Fresh exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- No use of team name, episode ID, seed, future information or opponent private state as an agent feature.
- Original final holdout remains sealed.
- No automatic hosted submission without a passed frozen promotion gate.
- Closed hypotheses stay closed unless genuinely new evidence invalidates the reason for closure; do not retune on their failed validation data.

## Immediate next actions

1. Finish run `34668446703` and classify CR080 failure mechanism; use it only to eliminate bad architecture classes.
2. Finish run `34669006417` and apply the frozen CR081 Gate A to the deep UMG corpus.
3. If Gate A passes, build one CR081 candidate and run fresh exact paired-seed validation against CR071M plus relevant current-lineage anchors.
4. Only a candidate that passes that frozen promotion gate becomes eligible for a hosted Kaggle probe.
