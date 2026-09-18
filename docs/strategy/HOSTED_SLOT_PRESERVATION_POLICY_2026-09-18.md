# Hosted Slot Preservation Policy — Kaggriculture — 2026-09-18

## Why this policy exists

Kaggriculture keeps only the **two most recent submissions active**. A third submission
retires the oldest active submission. The two active submissions are also the submissions
used for the final evaluation.

Kaggle staff further clarified that final Bradley-Terry evaluation uses episodes only
when **both agents from the episode remain active** at tournament time. Therefore retiring
a strong active submission is not a harmless bookkeeping operation: it discards that
submission from the active/final set and its episodes against later-deactivated opponents
do not contribute to the final tournament.

## Historical lesson: submission 56333577

Exact public V47 control submission:
`56333577`

Final frozen live rating:
**2387.9**

Before retirement:
- 36 listed public episodes;
- 35 externally attributable resolved games;
- 29 wins;
- 5 losses;
- 1 tie;
- external score rate 84.29%;
- 33 unique external opponents.

It was replaced before reaching the project's own 100-episode maturity standard.
Therefore 2387.9 is a strong real hosted result but not a converged estimate. It is
unknowable whether continued activity would have driven the rating materially higher or
lower.

This retirement was strategically premature.

## Binding slot policy

1. **Hosted is not an exploratory sensor.**
   Do not submit threshold variants, nearby operators, or mechanically interesting probes
   merely to observe live rating.

2. **Exploration must happen offline first.**
   Causal branch gates, autonomous runtime gates, package parity, opponent panels and
   first-party proposal search must do the experimental work before Kaggle slots are used.

3. **Two active slots are scarce state, not daily quota.**
   The 5/day submission limit is only a maximum. It is not a target and provides no reason
   to consume slots.

4. **Do not retire a record-setting or clearly strong active submission while its rating
   is still materially moving.**
   Default maturity requirement before voluntary replacement:
   - at least 100 public episodes, and
   - rating trajectory no longer moving materially over successive checkpoints,
   unless deadline pressure or a critical bug justifies earlier replacement.

5. **A challenger must earn the right to displace an active slot.**
   Before hosted submission, require:
   - hosted-faithful loader identity;
   - deterministic package parity;
   - positive causal W/L evidence;
   - autonomous runtime evidence on fresh seeds;
   - no unresolved catastrophic failure mode;
   - a concrete reason to believe the challenger can improve or hedge the active pair.

6. **Do not submit a new challenger merely because a current active bot has reached the
   earlier 32-game informative threshold.**
   32 games is sufficient for a first informative read, not sufficient reason to retire
   an active agent.

7. **Final pair discipline.**
   Near the deadline, preserve the two strongest, error-free and strategically
   complementary agents. Do not replace either for cosmetic live-rating rerolls.

## Current active pair

As of 2026-09-18:

CONTROL R2:
`56336025` — exact V47.

TREATMENT R2:
`56336027` — hosted-faithful V47 + O-RW1.

No additional Kaggle submission is authorized while these two are still maturing.

O-TW1 and later solver options remain offline until they have enough evidence to justify
displacing an active slot.

## Current maturity targets

- 32 external games/arm: first informative checkpoint only.
- 100 public episodes/arm: normal minimum maturity before voluntary replacement.
- If an active bot is setting a new project record and rating is still materially moving,
  continue observing beyond 100 when time permits rather than retire mechanically at 100.
