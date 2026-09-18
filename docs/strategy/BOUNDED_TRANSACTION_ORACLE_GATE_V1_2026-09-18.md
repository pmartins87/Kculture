# Bounded Transaction Oracle Gate V1 — 2026-09-18

## Question

Does exact counterfactual search over a **small legal transaction/market proposal set** have
enough W/L headroom on top of a complete strong adaptive agent to justify Policy/Value
distillation?

This is the first gate after closing the standalone exact-prefix router.

## Base organism

Candidate side: exact current public V47 source
`ahmedberatozer/kaggriculture-v47-reactive-market-coordination`,
packaged `main.py` SHA-256
`f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

V47 is used as a complete adaptive organism, not reduced to its tape library. The gate
does not persist its third-party source into the repository.

Opponent blocks:
1. exact V47 mirror;
2. exact current legacy V39
   `ahmedberatozer/kaggriculture-v39-ready-before-the-rush`,
   `main.py` SHA-256
   `708c7485fa964853b193f175dcd83020602c005e159ce82e38dc350b22e970c8`.

## Evaluation

Official `kaggle-environments==1.32.7`.

Fresh seeds: `62001, 62002`.  
Both seats.  
Two expert blocks.  
Eight baseline matchups.

For each baseline matchup, choose at most two eligible intervention states:
- V47 base action contains at least one `SELL`;
- step is between 24 and 671 inclusive;
- selected states are separated by at least 72 turns.

This yields at most 16 branch states.

Every matchup is replayed once with no intervention from fresh agent instances. Final
rewards must match the discovery baseline exactly. Any replay mismatch invalidates that
matchup/gate rather than becoming strategic evidence.

## Proposal family

At one selected state only, preserve V47 farmer action and hand actions exactly. Candidate
proposals modify only the **current turn market list** derived from the exact V47 action:

- BASE — no change;
- swap the first two SELL orders;
- reverse the SELL subsequence while preserving non-SELL positions;
- move the first SELL order to the front of the market list;
- move the last SELL order to the front of the market list;
- defer the first SELL by removing it for this turn only;
- defer the last SELL by removing it for this turn only.

Deduplicate action-identical proposals. No new product, quantity, buy, hire or physical
action may be invented. Maximum market cardinality remains legal.

At the intervention step the freshly replayed V47 base action must hash exactly to the
action recorded in discovery. Otherwise the branch is invalid.

After that one intervention, the exact V47 policy resumes unchanged for all later turns.

## Offline oracle

For each branch state, evaluate every proposal to terminal completion from a fresh exact
replay. The offline oracle chooses lexicographically:

1. W/L outcome;
2. final margin.

Terminal future information is used **only to create offline labels/headroom metrics**.
No runtime candidate may observe seed, future RNG, terminal outcome, opponent identity or
private opponent state.

## Frozen headroom gate

Mechanical PASS requires:
- exact source hashes;
- all baseline/parity episodes DONE/DONE;
- replay identity final rewards exact;
- all candidate branches DONE/DONE;
- target-step base-action identity exact;
- at least 12 valid branch states.

Strategic headroom PASS if mechanical PASS and either:
- oracle W/L score-rate delta over BASE across branch states >= `+0.125`; or
- at least 2 BASE losses are converted to oracle wins.

Interpretation branches:

1. `TRANSACTION_ORACLE_WL_HEADROOM_PASS`:
   freeze branch-state/proposal labels and advance to observation-only proposal/value
   distillation on fresh held-out seeds.

2. `TRANSACTION_ORACLE_MARGIN_ONLY`:
   no sufficient W/L headroom but mean oracle margin delta is positive. Close this simple
   sale-order/one-turn-deferral family as a competitive search space and expand to
   multi-turn conserved transactions/guards.

3. `TRANSACTION_ORACLE_NO_HEADROOM`:
   no meaningful W/L or margin headroom. Close this family and move directly to richer
   transaction bundles / execution repairs.

No Kaggle submission is authorized by this offline oracle gate.
