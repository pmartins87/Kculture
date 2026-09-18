# First-Party Ready-Wool Sale Causal Gate — 2026-09-18

## Why this gate exists

Adaptive Wrapper Oracle V2b produced the first Prize-Solver W/L headroom PASS:
the only promoted proposal was Ready Stock adding `SELL WOOL 2` while V47's farmer and
hands were identical and V47's market action was empty.

Before training a selector or depending on third-party Ready Stock code, isolate the
causal rule using only legal own-state information.

## Base policy

Exact current public V47:
`ahmedberatozer/kaggriculture-v47-reactive-market-coordination`
SHA-256
`f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

Third-party source is transient benchmark infrastructure only.

## First-party option O-RW1

At an eligible state, obtain the exact V47 action first.

Eligibility uses only the candidate's legal current observation and its own action:
- V47 current `market` list is exactly empty;
- own private `shed.WOOL >= 2`;
- step is 0..671.

Counterfactual treatment changes only the current market action:

`[] -> [["SELL","WOOL",2]]`

Farmer and hands must remain byte/canonical identical to V47.
The sale uses stock already present in the current shed; no projected same-turn stock,
future route knowledge, opponent identity, hidden seed or future state is used.

After that one intervention, exact V47 resumes unchanged.

## Opponent panel

Fresh current public agents:
1. V47 mirror, exact SHA above.
2. V48 Clear-the-Queue:
   `ahmedberatozer/kaggriculture-v48-clear-the-queue`,
   SHA `4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96`.
3. Tactical Memory rank-20:
   `web3cainiao/kaggriculture-v21-tactical-memory`,
   SHA `630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054`.

Tactical Memory is included as an additional lineage rather than another modern-41
wrapper.

## Evaluation

Exact `kaggle-environments==1.32.7`.

Fresh seeds: `64001,64002,64003,64004`.  
Both seats.  
24 baseline matchups.

Discovery records all eligible O-RW1 states. Select at most the first two per matchup,
separated by at least 72 turns. Each selected event is evaluated independently from a
fresh full replay with exactly one O-RW1 intervention.

Fresh V47-only replay must reproduce discovery final rewards exactly.
At the branch step, the fresh V47 base action and the recorded base action must match
exactly. Any mismatch invalidates the gate.

## Metrics

Primary: paired W/L score difference treatment minus BASE at each one-intervention branch.

Secondary:
- paired terminal margin delta;
- positive / negative / neutral intervention counts;
- distribution by opponent block and step;
- whether treatment converts loss/tie to win or win to non-win.

## Frozen decision

Mechanical PASS:
- exact source hashes;
- zero episode/runtime/action-identity failures;
- exact discovery/replay parity;
- at least 24 valid branch states.

Strategic branches:

### `READY_WOOL_CAUSAL_PASS_SAFE_OPTION`
Require all:
- mean W/L delta > 0;
- at least 2 non-win -> win flips;
- zero win -> non-win regressions;
- each of at least 2 opponent blocks has nonnegative mean W/L delta.

Then freeze O-RW1 as a first-party proposal option and evaluate an always-on guarded
runtime candidate on fresh seeds.

### `READY_WOOL_CAUSAL_HETEROGENEOUS`
There is both positive and negative W/L value or a material regression block.
Do not ship always-on. Freeze observation-state labels and train/derive a selector.

### `READY_WOOL_MARGIN_ONLY`
No W/L gain, but positive mean terminal-margin delta and no major W/L regressions.
Retain as economic evidence only; do not promote.

### `READY_WOOL_NO_HEADROOM`
No positive W/L or margin headroom. The Ready Stock V2b benefit depended on additional
context not captured by this simple first-party state rule; move to richer labelled
proposal-trigger learning.

No Kaggle submission is authorized by this gate.
