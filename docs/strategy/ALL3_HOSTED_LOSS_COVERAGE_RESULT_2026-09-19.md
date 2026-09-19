# ALL3 Coverage of Mature O-RW1 Hosted Loss Corpus — 2026-09-19

## Binding run

Workflow:
**`35465395838`**.

The earlier run `35465296314` is non-binding mechanical-invalid because `kagglehub` was omitted
from the analysis environment. The rerun changed only that dependency.

Corpus:
- 128 newest mature O-RW1 public replays;
- 45 wins / 82 losses / 1 tie;
- 118 unique opponents in the replay forensic summary.

This analysis reconstructs how ALL3 would alter the recorded O-RW1 action stream. It is a coverage
census, **not** a counterfactual outcome simulator.

## Coverage

Across the 82 O-RW1 losses:
- mean reconstructed ALL3 changed turns: **152.02**;
- mean LQ2 changed turns: **151.07**;
- TW1 would fire in **82/82**;
- zero losses had zero ALL3 action changes.

At step 336:
- 49/82 losses were still ahead in public farm-money delta;
- 32/82 were behind;
- one was exactly tied.

Thus most mature O-RW1 losses are not simply games that were already irrecoverably lost before LQ2.

## Early residual subset

A conservative residual-hard descriptive subset was defined as:
- losing replay;
- already behind at/after step 336;
- first reconstructed ALL3 change at or after step 336.

Only **9/82 losses** meet that definition.

Those nine have:
- mean terminal margin **-1,008.67**;
- mean money delta around step 336 **-218.56**;
- mean first ALL3 change around step **338**.

## Interpretation

This corpus supports two conclusions:

1. ALL3 materially changes the action stream of essentially all mature O-RW1 losses, so O-RW1's
   old loss population should not be treated as ALL3's current failure set.

2. A small early/macro residual exists, but it is not large enough to justify jumping directly into
   broad macro-policy surgery.

After ALL3 itself reached 34 resolved external games with six actual losses, those six ALL3 losses
became the primary next-option discovery population.

No runtime identity information is promoted from this analysis.
