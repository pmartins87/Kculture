> **2026-09-11 amendment:** Governance, hosted slot accounting and minimum
> execution gates below remain binding. The 09/09 immediate actions and candidate
> state are superseded by STATUS.md, ROADMAP.md and the CR080 protocol. CR071M is
> already submission 56124705. CR078/CR079 are closed; current work is CR080.

# Kculture execution contract — 2026-09-09

## Mission

Maximize expected probability of a prize-winning final result in Kaggriculture. The operational target remains to close the gap to the current ~2700+ public frontier and pursue a top-10 result, not merely to produce locally respectable agents.

## Governance: questions are not commands

1. A user question, concern, or hypothetical does **not** change the technical plan by itself.
2. A strategy change requires either:
   - explicit user instruction, or
   - new evidence that crosses a predeclared gate.
3. Even with an explicit user instruction, the technical lead must state when the requested action appears strategically inferior and explain why before executing it when confirmation is still possible.
4. Do not infer an unstated user decision and silently act on it.
5. Every material change of direction must be recorded with: evidence, decision, rejected alternatives, and next branch.

## Official competition constraints that drive strategy

- Final submission deadline: 2026-09-30 23:59 UTC.
- Daily submission cap: 5.
- Only the latest two submissions remain active.
- The latest two are used for final evaluation; team rank is based on the better of the two, so the second active slot is a hedge.
- Final evaluation is a post-deadline Bradley-Terry tournament over active submissions/episodes; live rating is calibration evidence, not the final objective.
- Primary local metric: seat-balanced W/L / score_rate. Money margin is diagnostic only.

## Two-slot hosted policy

Treat the two active Kaggle submissions as scarce **active slots**, not as five disposable daily attempts.

### Slot A — incumbent

Keep the strongest hosted-supported materially relevant agent active unless there is evidence that a replacement is stronger or unless a deliberate control is required.

### Slot B — challenger / hedge

Use for a materially different candidate that passed the minimum hosted-probe gate below, or for a deliberately complementary hedge.

### Daily cap policy

- Five/day is a ceiling, not a target.
- Do not burn slots on byte-identical rerolls or tiny parameter variants.
- Do not allow a qualified, materially different candidate to sit unsubmitted for >24h merely because more local testing is possible.
- Normally use at most one new challenger in a decision epoch; a second same-day submission requires a distinct hypothesis or a mechanical recovery.
- Never submit a new challenger without knowing which active submission it will retire.

## Minimum gate for a hosted probe

A candidate is eligible for hosted calibration when all are true:

1. Exact `kaggle-environments==1.32.7` execution and package entrypoint pass.
2. Both seats tested; zero mechanical errors in the promotion sample.
3. Material strategic difference from the current hosted active candidate, or a clearly predeclared control.
4. At least one fresh exact-reference validation sample after candidate freeze.
5. No material regression on designated guardrail opponents, unless the candidate is intentionally a complementary hedge and the tradeoff is recorded.
6. There is a concrete hosted question that local testing cannot answer well enough.

A hosted probe does **not** require proving the candidate is final-best. Hosted evidence is itself part of development.

## Current candidate: CR071M PRESALE1

Frozen package:

`CR071M_CR053_PRESALE1_SEATSAFE_V1.tar.gz`

SHA256:

`dbc6fc2b2c3673b1d9fc36e103b8369a53c7f2cc33381e11a3cb5f769bebe652`

Evidence already observed against CR053 across four independent batches:

- screen: PRESALE1 20-12; PARENT 13-19;
- fresh confirmation: 38-26 vs 24-40;
- broad-frontier set: 36-28 vs 32-32;
- fourth fresh set: 44-20 vs 36-28.

Diagnostic combined total:

- PRESALE1 138-86 (61.61%);
- PARENT 105-119 (46.88%);
- 112 paired seeds / 224 games per policy.

CR071O `opp.money > 190` selector is rejected and that selector hypothesis is closed. This does **not** close CR071/PRESALE1 development as a whole.

**Hosted status:** CR071M PRESALE1 is qualified for one controlled hosted probe now.

## Active local run

`cr071-presale1-deep-frontier-v1`, run `34359535052`.

- 64 fresh paired seeds per H2H;
- 128 games per matchup;
- 11 H2Hs;
- 1,408 exact-reference games total;
- PARENT and PRESALE1 against CR053/CR061/CR065/CR068A/CR068B;
- PRESALE1 direct vs CR070A.

This run must continue even while the hosted probe runs. The hosted probe and local deep validation answer different questions.

## Predeclared decision tree after deep-frontier + hosted evidence

### A. Deep frontier strong + hosted strong

Definition:
- PRESALE1 beats PARENT materially on the panel;
- no material guardrail regression;
- hosted trajectory is competitive relative to current active baseline after enough episodes to be informative.

Action:
1. promote PRESALE1 to incumbent candidate;
2. freeze its exact hosted provenance;
3. use the second active slot for the next **independent architectural challenger**, not a micro-threshold derivative;
4. start R5/R6 architecture-gap work against current 2700+ public agents and hosted losses.

### B. Deep frontier strong + hosted weak

Action:
1. hosted evidence outranks the local proxy for prize decisions;
2. preserve PRESALE1 as mechanistic evidence, not champion;
3. inspect hosted losses/opponent families and quantify where local panel is miscalibrated;
4. next candidate must target that demonstrated hosted failure, not simply add more seeds to the same local matchup;
5. keep one active slot on the best hosted incumbent while testing one distinct challenger.

### C. Deep frontier weak/neutral + hosted strong

Action:
1. do not discard the candidate merely because local panel is neutral;
2. preserve hosted candidate active long enough to collect informative episodes;
3. identify which hosted opponent families benefit and add them to calibration/replay analysis;
4. redesign local panel around hosted-relevant families before the next challenger.

### D. Deep frontier weak + hosted weak

Action:
1. reject PRESALE1 as prize-scale direction;
2. no further PRESALE1 microvariants;
3. pivot to independent architecture work using current high-performing public agents and current hosted losses;
4. next hosted submission requires material architectural difference.

### E. Hosted result still immature

Do not read an early live rating as final strength. First review when roughly >=60 hosted episodes are available or after about 5 hours if episode count is not exposed; stronger review near >=150 episodes / 1-2 days. Compare same-age trajectories when possible. These timing numbers are heuristics, not official Kaggle guarantees.

## Independent architecture branch — always active

Regardless of whether PRESALE1 passes, pursue an independent path intended to close the ~1600 -> ~2700+ gap.

Priority order:

1. Refresh current public frontier and identify strongest reproducible public agents/packages/notebooks.
2. Freeze exact package/source identities and current public scores as time-stamped evidence.
3. Reproduce them in exact reference locally and compare to CR070A/PRESALE1 over both seats.
4. Perform action/route/market/production decomposition to identify large structural differences, not cosmetic code differences.
5. Rank candidate mechanisms by plausible W/L ceiling and hosted relevance.
6. Run cheap causal ablations first; only then build combined candidates.
7. Use official/public hosted episode datasets and our own hosted losses to recalibrate the opponent panel.
8. A new architectural candidate gets a hosted slot once it crosses the minimum hosted-probe gate; do not wait for exhaustive perfection.

## Research budget / stopping rules

- A hypothesis gets: discovery -> one fresh confirmation -> broad validation only if still promising.
- If a predeclared fresh gate fails, do not tune thresholds on that validation set.
- A failed narrow hypothesis is closed; the project continues on the next highest-value hypothesis.
- A candidate may still go hosted after a mixed local result when it is materially different and hosted information value is high; that decision must be explicit.
- Do not run tests whose result would not change a decision.

## Communication contract

Every substantial update to the user must end with exactly what the user should do:

- take a concrete action now;
- send `continue` so work can proceed/check;
- or wait, with the explicit event/time that ends the wait.

When a question from the user exposes a process concern, answer the concern first. Do not silently turn it into a strategy change.

## Current immediate actions — 2026-09-09

1. User submits the exact frozen CR071M PRESALE1 package as one hosted challenger.
2. Deep-frontier run `34359535052` continues to completion; do not cancel it because of the hosted probe.
3. While both run, refresh/analyze the current public 2700+ frontier and prepare the next independent architectural research target.
4. When the PRESALE1 submission ID arrives, record it in `docs/SUBMISSION_LEDGER.md` immediately.
5. First hosted checkpoint: approximately 60 episodes, or ~5h after submission if episode count cannot be read; do not wait days without inspecting.
6. Apply decision tree A/B/C/D above after hosted + deep-frontier evidence; do not invent a new path post hoc unless new evidence truly falls outside the tree, in which case document the exception before acting.
