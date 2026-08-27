# KEXP-20260827-056 — TOMATO post-yield visit audit

Status: **COMPLETE / CANDIDATE AUTHORIZED**

Run: **33102950487**  
Artifact: **9659393076**  
Artifact digest: **sha256:cc92b6b0e77f406e5799a7ce60edd5d1fd968280be7552ba306ad120f42f5671**

KEXP-053 identified long-lived WHEAT slots; KEXP-055 showed that five structural slot families do not collide with a later PLANT. KEXP-056 tested whether the existing R4B route revisits those tiles after TOMATO's 192-turn first-yield threshold but before the original WHEAT HARVEST.

## Result

Across development + exploratory live-meta open distributions, 26 qualifying long-lived slot occurrences were observed in 10 episodes. Every occurrence had a post-maturity WATER visit. Eighteen had a WATER visit at least 24 turns before the base WHEAT harvest.

Three exact slot families passed the cross-distribution routing gate:

- `262@(0,4)`: first post-maturity WATER at state 494; base harvest 543; 3/3 development and 3/3 live-meta occurrences were early opportunities;
- `310@(9,7)`: first post-maturity WATER at 671; base harvest 708; 3/3 development and 3/3 live-meta;
- `334@(5,9)`: first post-maturity WATER at 622; base harvest 690; 3/3 development and 3/3 live-meta.

The two other structurally safe families were revisited too late for the predeclared early-opportunity rule:

- `451@(7,3)`: WATER 667, base harvest 680;
- `477@(0,9)`: WATER 687, base harvest 688.

Overall mean lead from first post-maturity WATER to base harvest was 37.69 turns. The frozen gate result is therefore **PASS**: a bounded TOMATO candidate is mechanically authorized on the three passing slot families.

This is still mechanics/routing evidence only. It does not prove that replacing the WHEAT lifecycle with TOMATO improves terminal money, and it does not authorize validation, held-out access, or hosted submission by itself.
