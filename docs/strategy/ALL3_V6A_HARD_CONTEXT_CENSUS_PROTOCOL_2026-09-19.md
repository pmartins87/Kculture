# ALL3 V6A Hard-Context Census — Protocol — 2026-09-19

## Purpose

V5 one-turn localized physical proposals produced:
- 32 branch states;
- zero nonwin->win flips;
- mean margin headroom only;
- the only non-winning base trajectory was V48 seed 75002 seat 0, margin -26.

Before escalating to a more expensive 2–3-turn physical continuation oracle, locate a fresh set of
ALL3 non-win contexts across the diverse seven-family V2 league.

This census contains **no intervention** and cannot authorize a submission.

## Executed agent

Exact ALL3:
- hosted-faithful V47;
- O-RW1;
- O-TW1;
- O-LQ2.

## Opponent panel

The frozen V2 seven-family league:
1. V47 mirror;
2. Ready Stock;
3. V48;
4. router_2715;
5. Conditional Memory;
6. Tactical Memory;
7. Best Market.

All packages remain exact SHA-pinned public agents already used in V2.

## Fresh seed batch A

Seeds:
`75101..75108`.

Both seats.

Total:
7 opponents × 8 seeds × 2 seats = **112 exact-engine games**.

## Output

For every matchup record:
- opponent/family;
- seed;
- seat;
- ALL3 reward/opponent reward;
- terminal margin;
- W/T/L score.

Aggregate:
- W/T/L by opponent;
- non-win contexts;
- close-win contexts (margin <= +500) for diagnostics only.

## Selection for V6 continuation discovery

Primary hard contexts:
- every fresh base LOSS or TIE.

Rank:
1. loss before tie;
2. absolute terminal margin ascending inside outcome class, so close failures are tested first;
3. opponent key, seed, seat for deterministic tie-break.

Freeze at most **12** primary hard contexts for V6.

Diversity preference:
- retain at least one non-win from every opponent family that produced a non-win before taking second
  contexts from any family.

If fewer than **4** total non-win contexts are found:
- decision = `V6A_EXPAND_HARD_CENSUS`;
- do not branch on close wins as substitutes;
- add a second untouched seed batch before V6.

If >=4 non-win contexts:
- decision = `V6A_HARD_CONTEXTS_READY`;
- freeze the selected context list;
- proceed to the bounded 2–3-turn localized physical continuation oracle.

No opponent identity is permitted as a deployment/runtime feature. Opponent labels are offline
experiment metadata only.
