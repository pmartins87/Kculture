> **2026-09-11 update:** The historical next-sequence section below is superseded.
> CR079 simple SpaTaro 1-NN failed; CR080 Mengfei daily-route bridge passed its
> initial exact screen 10-6 and is in confirmation run 34655496708. See STATUS.md.
> Current snapshot leader is Majkel1337 3152.9, SpaTaro 3049.7; the table below
> remains the earlier timestamped snapshot, not current ranking.

# Current-meta replay mining — 2026-09-10/11

## Why this replaces blind CR071 micro-tuning

Authenticated hosted evidence now shows that CR071M is not failing because of one isolated late-turn bug. Its 208 hosted episodes contain a broad current-meta collapse against stronger/distinct policy families. The next line therefore mines public hosted replays first and only then freezes a new candidate hypothesis.

Primary promotion metric remains seat-balanced W/L / score_rate in `kaggle-environments==1.32.7`. Money is diagnostic only.

## Authenticated current leaderboard snapshot

The corrected CLI parser walked the current top 15 and successfully accessed `team-submissions -> episodes -> replay` for every team. Snapshot around 2026-09-11 02:08 UTC:

1. SpaTaro — 3142.3
2. feel the agi — 3038.2
3. ymg_aq — 3032.0
4. Otter Vibe — 3026.6
5. Majkel1337 — 3015.8
6. binghua — 2987.0
7. Gleb Tumanov — 2968.0
8. Mengfei Li — 2962.9
9. redblackbst — 2956.7
10. 薄荷喵呜 — 2955.8
11. keiz — 2955.5
12. Himanshu Kumar — 2955.1
13. mtmr_s1 — 2948.9
14. c0nrad — 2944.2
15. 3정훈 — 2935.9

This establishes that ~3000 is currently top-five territory, not a hypothetical target.

## Top-15 replay access result

Run `34553397276`:

- leaderboard parse: PASS
- 15 team IDs resolved
- 30 recent submissions enumerated
- 60 public hosted replays downloaded (2 per selected submission)
- cross-team replay access: PASS

Artifact: `kaggle-api-meta-scout-v1`, ID `10181691343`.

## Important lineage findings

### Dominant hostile family is genuinely high-meta

The public policy family previously fingerprinted from CR071M losses by the opening

- step 0: `BUY_PRODUCT WHEAT 13 -> SELL WHEAT 13 -> BUY_PRODUCT WHEAT 13`
- step 1: `SELL WHEAT 13`, `BUY_PRODUCT WHEAT 5`, five hires, two cows, two sheep

is not merely a mid-table artifact. It appears in the sampled current top 15, including 薄荷喵呜 (~2956) and Himanshu Kumar (~2955). In CR071M's own hosted corpus this opening family produced 1 win / 25 losses over 26 observed games.

Several other high-meta agents use related but different opening price/market manipulations, e.g. Gleb Tumanov and redblackbst.

### The closest high-scoring bridge is Mengfei Li, not the radically different leader

Mengfei Li's current sampled policy starts exactly like the CR070A/CR071M lineage:

- step 0: `BUY_PRODUCT WHEAT 13`
- step 1: `SELL WHEAT 9`, buy 7 wheat seed + 12 melon seed, five hires, two cows, two sheep

Yet its current leaderboard rating is ~2963.

The two sampled replays from current submission `56047440` are action-identical through step 225 and then branch on public world state. They differ substantially from frozen CR070A after the midgame. In one sampled current replay only 286/719 actions match frozen CR070A MAIN; in the other only 278/719 match. This makes this lineage a high-value *bridge*: same proven early architecture, materially stronger current mid/late policy.

Observed branch examples:

- step 226 branches goose vs cow according to public shop/world state;
- by step 288 it uses aggressive cash-flow conversion and seven-worker expansion;
- subsequent routes diverge materially according to unlocked shops and observed economy.

We will not treat a public replay as causal proof and will not submit an unchanged harvested trajectory. The purpose is to recover mechanisms/branches, implement an evidence-backed derivative, and test it on fresh seeds in both seats.

### SpaTaro is a separate frontier

SpaTaro (~3142) is much more state-adaptive already within the first 100 turns in the 4 sampled replays and uses a different opening/farm structure. A full current replay corpus is being collected separately. This is the likely path beyond the ~2960 bridge if the nearer-lineage reconstruction works.

## CR078 disposition

CR078 late mirror-breaker is closed. Fresh exact-reference screen: 5-23-36 vs exact CR071M parent, score_rate 0.3594, CI95 [0.28125, 0.4375]. Decision: `DO_NOT_SUBMIT_CR078_SCREEN_FAILED`.

## Frozen next research sequence

1. Collect a broad current Mengfei sample (`56047440`) and full current SpaTaro corpus (`56114097`).
2. Reconstruct branch structure and quantify action/state differences against frozen CR071M/CR070A.
3. Prefer the closest strong mechanism first (Mengfei lineage) because it minimizes uncontrolled architectural changes.
4. Freeze exactly one CR079 hypothesis before fresh validation.
5. Test CR079 against parent + current hostile-family controls + historical guardrails, both seats, fresh seeds.
6. Only after an exact-reference gate passes consider a hosted probe.

No CR078 retuning and no automatic hosted submission are authorized by this research step.
