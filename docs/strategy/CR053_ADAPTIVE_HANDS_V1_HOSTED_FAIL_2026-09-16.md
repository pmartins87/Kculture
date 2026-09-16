# CR053 Adaptive Hands V1 — hosted structural failure (2026-09-16)

## Hosted observation

Submission `56282257` (Adaptive Hands V1) shows a strong downward hosted trajectory after 136 games in the user-provided Game History view. The screenshot does not expose a sufficiently unambiguous current rating value to record one here. The result is nevertheless clearly a catastrophic competitive regression rather than a marginal loss.

## Root cause

The intervention was architecturally incoherent.

The candidate preserved CR053's static farmer action and static market action tape, but after step 47 replaced every hand action with a limited adaptive dispatcher that only handled:

- FEED
- WATER
- CARE
- COLLECT_FERTILIZER
- HARVEST
- WHEAT pickup/routing

However, the original CR053 hand tape after step 47 still contains essential state-forming and logistics actions:

- PLANT: 199
- FERTILIZE: 148
- PLACE: 144
- DROP: 64
- DIG: 41
- BUILD_COOP + BUILD_PASTURE: 9
- PICKUP: 194

The replacement therefore deleted hundreds of actions that the retained farmer/market tape assumed had happened. Once the hand-created state diverged, subsequent static farmer and market actions were often invalid, mistimed, or economically incoherent. The entire replay-derived route cascaded away from its historical state trajectory.

## Interpretation

This failure does **not** show that adaptive worker dispatch is intrinsically bad. It shows that a state-changing adaptive layer cannot safely be grafted onto a static replay backbone while leaving the rest of the replay tape unchanged.

The distinction with O1 is important:

- O1 only reorders an existing market multiset and largely preserves the physical trajectory/state assumptions of CR053.
- Adaptive Hands changes the physical state trajectory and therefore invalidates downstream replay assumptions.

## Binding methodology rule

Do not use CR053 as the host for any intervention that materially changes physical state, worker positioning, crop/animal lifecycle, land/building setup, inventory logistics, or future action preconditions unless the downstream policy is also made state-adaptive.

CR053 remains useful only for:

1. contemporaneous hosted control; and
2. narrowly state-preserving interventions.

Structural candidates aimed at prize-level performance must be end-to-end state-adaptive rather than replay-tape hybrids.

Decision: `CR053_ADAPTIVE_HANDS_V1_CATASTROPHIC_FAIL_CLOSE_REPLAY_HYBRID_PHYSICAL_PATCHING`.
