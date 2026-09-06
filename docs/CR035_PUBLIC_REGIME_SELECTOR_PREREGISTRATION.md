# CR035 — Public Regime Selector Tournament

## Objective

Test a materially new architecture on the exact already-open CR029 elite panel: keep the strong CR029 `full_recent_top` policy for the opening, then use a public-only regime classifier at clock 24 to decide whether to remain on CR029 or switch to one complete elite tape.

This is an **actual switched-agent evaluation**, not an oracle recombination of final scores. Therefore any trajectory mismatch caused by switching from one open-loop tape to another is paid by the candidate during simulation.

## Frozen classifier

CR034 found perfect leave-one-episode-out separation of the two observed elite strategy families at horizon 24 using only public state. The frozen full-data stump is:

- feature: own public farm money (`self_money`)
- clock: 24
- threshold: `35.5`
- `self_money > 35.5` => classify as `keiz`
- otherwise => classify as `Jesse Bullard`

The classifier is latched once at clock 24 and is not retuned in CR035.

## Runtime policy

For every candidate alternate tape:

1. clocks 0..23: use the exact CR029 `full_recent_top` tape;
2. at clock 24, read only own public farm money from the current observation;
3. if classified `Jesse Bullard`, stay on CR029 for the rest of the game;
4. if classified `keiz`, switch immediately to the candidate complete elite tape at the same clock index and remain on it for the rest of the game.

The runtime does **not** read opponent/team name, episode id, seed, submission id, source rank, or any future information. The alternate tape identity is fixed at package construction time, not selected from opponent identity.

## Candidate pool

Exactly the 12 elite winner tapes already frozen in `configs/cr031_elite_round_robin.json`, each with its existing provenance hash. CR029 itself is evaluated as rank 0 control.

## Evaluation panel

Exactly the 12 already-open CR029 source scenarios in `configs/cr031_elite_round_robin.json`, both seats, for 24 games per candidate. No fresh or held-out seed is opened by this screen.

## Promotion gate

A selector is shortlisted only if all are true relative to paired CR029 control on the same 24 games:

- mechanical completion: 24/24 games DONE and zero errors;
- classifier correctness: 24/24 family classifications match the already-known panel labels;
- total W/L score gain >= `+2.0`;
- favorable W/L conversions >= `2`;
- unfavorable W/L conversions <= `2`;
- mean paired reward-delta gain > `0`;
- Jesse branch is action-equivalent to CR029 and therefore has zero W/L conversions.

Among passing candidates, rank by total score gain, net favorable conversions, and mean paired reward-delta gain.

## Frozen decision rule

- Any pass => `CR035_SHORTLIST_READY`; top candidate proceeds to a separate confirmation/package step without threshold retuning.
- No pass => `CR035_NO_SELECTOR_PROMOTION`; retire this two-family selector architecture on this panel rather than tuning the 35.5 threshold against outcomes.

## Leakage firewall

- source scenarios: already open before CR035;
- fresh validation: untouched;
- held-out set: untouched;
- runtime identity features: forbidden;
- threshold tuning after seeing CR035 outcomes: forbidden.
