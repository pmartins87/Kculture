# ALL3 V11B Hosted Loss Signature Atlas Protocol — 2026-09-20

## Status

Descriptive / hypothesis-generation only.

This analysis follows the mature V11A hosted refresh and may inspect outcome-associated replay structure. Therefore it is **not a causal preregistration** and cannot itself promote an option.

## Source

V11A workflow `35518801971`, ALL3 submission `56367770`, 128 newest public replays.

## Questions

1. How rigid is ALL3's own macro trajectory across the hosted population?
2. Which legal public opponent-relative state signatures distinguish ALL3 losses from wins?
3. Is there a repeated public competitive regime suitable for a later causal option-discovery gate?

## Frozen descriptive checkpoints

Steps:
`120, 240, 336, 360, 408, 456, 480, 504, 552, 600, 648, 672, 696, 718`.

At each checkpoint record:
- own/opponent public money;
- unlocked quadrants;
- plant/pasture counts;
- crop counts by WHEAT/CARROT/TOMATO/STRAWBERRY/MELON;
- animal counts COW/SHEEP/GOOSE;
- own-private shed units/value, carried units, seed units;
- own-minus-opponent gaps.

Outcome cohorts:
- all wins / all losses;
- close loss [-1000,0);
- close win (0,1000];
- severe loss <= -3000;
- strong win >= 3000.

## Public crop-shift signatures

Descriptively report:

- `opp_carrot_adv`: opponent public CARROT plant count > own CARROT count.
- `opp_carrot_adv4_wheat_def4`: opponent CARROT - own CARROT >=4 AND own WHEAT - opponent WHEAT >=4.

These signatures are observational and are not yet runtime rules.

A useful discovery signal is present if, at some checkpoint <=600:
- support >=8 hosted games;
- loss rate >=0.90.

Decision:
- qualifying signal => `V11B_PUBLIC_CROP_SHIFT_REGIME_SIGNAL`;
- otherwise => `V11B_NO_SIMPLE_PUBLIC_REGIME_SIGNAL`.

Any subsequent candidate must be tested causally against executable public agents on untouched seeds before it can enter the option library.

Opponent identity is offline metadata only and prohibited as runtime policy input.
