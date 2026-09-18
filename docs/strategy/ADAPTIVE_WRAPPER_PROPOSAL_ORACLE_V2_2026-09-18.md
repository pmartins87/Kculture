# Adaptive Wrapper Proposal Oracle V2 — 2026-09-18

## Purpose

V1 proved that synthetic SELL permutation / one-turn deferral has no headroom on the
complete V47 policy at the tested states. V2 changes the **proposal generator**, not the
exact-search architecture.

Question: do different strong public adaptive wrappers that share the same modern
programme chassis produce locally different market actions which an exact oracle can
select state-by-state to improve W/L over V47?

## Base organism

Exact current V47:
`ahmedberatozer/kaggriculture-v47-reactive-market-coordination`
SHA-256 `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

V47 remains the executed policy on every non-intervention turn.

## Shadow proposal generators

All are current public Top-30 agents from the modern 41-route lineage and are used only
transiently as proposal generators:

- Ready Stock / Earlier Sales:
  `alperen5252525/kaggriculture-ready-stock-earlier-sales`
  SHA `45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017`.
- Market-Smart:
  `tetsutani/market-smart-farming-kaggriculture`
  SHA `f6a756cfb900b9d5f499905d596b63f1fde2445342ac4b1ae04e353739bd62d2`.
- V46 first-turn microstructure:
  `ahmedberatozer/kaggriculture-v46-first-turn-microstructure-and-s`
  SHA `735c370383b70d3bf3aac792f2c147e0afc99166fc9f253ede10e8a030acedb6`.
- V48 clear-the-queue:
  `ahmedberatozer/kaggriculture-v48-clear-the-queue`
  SHA `4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96`.
- Shop-Aware:
  `tetsutani/shop-aware-farming-kaggriculture`
  SHA `411875c97d6a178ec4df59b696b13708ba2fac754cae924851395a0578ca983d`.

No third-party source is committed or uploaded as an artifact by this gate.

## Shadow semantics

During a discovery V47 trajectory, every proposal generator receives the same legal
candidate observation on every turn but its action is not executed.

A proposal is admissible only when:
- its farmer action exactly equals V47;
- its hands actions exactly equal V47;
- its market action differs from V47;
- market cardinality remains <= 10.

Thus V2 searches only a **one-turn market intervention** while preserving the complete V47
physical programme.

Proposal actions are deduplicated by exact canonical action. Multiple wrapper sources may
alias the same proposal.

## Evaluation

Exact `kaggle-environments==1.32.7`.

Fresh seeds: `63001, 63002`; both seats.

Opponent blocks:
1. exact V47 mirror;
2. exact V39 legacy adaptive agent.

Eight baseline matchups.

Select at most two proposal-disagreement states per matchup:
- step 0 through 671;
- at least one admissible non-V47 market proposal;
- selected states separated by at least 72 turns;
- earliest qualifying states win.

Discovery with shadow agents must reproduce a fresh V47-only replay's final rewards
exactly. Otherwise the matchup is invalid.

For every branch proposal, replay the whole episode from fresh agents. The selected shadow
generator is called on every pre-branch observation to reconstruct its internal memory.
At the target step both the V47 base action and the shadow proposal action must hash
exactly to discovery. Execute the shadow market action once; V47 resumes unchanged
afterwards.

## Offline oracle and gate

Oracle chooses lexicographically by:
1. W/L score;
2. final margin.

Mechanical PASS requires:
- all source hashes exact;
- zero incomplete/error episodes;
- exact discovery/replay parity;
- exact target base/proposal action identity;
- at least 8 valid branch states.

Strategic headroom PASS if mechanical PASS and either:
- oracle W/L score-rate delta >= `+0.125`; or
- at least 2 BASE non-wins (loss or tie) become oracle wins.

Frozen outcomes:

- `WRAPPER_PROPOSAL_WL_HEADROOM_PASS`:
  freeze proposal labels and advance to observation-only proposal/value distillation.
- `WRAPPER_PROPOSAL_MARGIN_ONLY`:
  close one-turn wrapper switching as a W/L search space; expand to multi-turn conserved
  transaction bundles/guards.
- `WRAPPER_PROPOSAL_NO_HEADROOM`:
  close this one-turn proposal ensemble and move to multi-turn transaction search.
- mechanics invalid: no strategic verdict.

No Kaggle submission is authorized by V2.
