# V26B Outcome Router — Persistent Policy vs Strategy Reassessment — 2026-09-21

## Status

PRE-REGISTERED while binding V26B workflow `35660845547` is still running, before reading any competitive V26B outcome.

This document freezes the immediate next branch.

## Route A — V26B_CONSENSUS_POLICY_HEADROOM

If and only if binding V26B returns:
`V26B_CONSENSUS_POLICY_HEADROOM`.

Open exactly one family:

**V27A_CONSENSUS_POLICY_DISTILLATION**

Goal:
replace the 12-teacher runtime ensemble with one first-party persistent policy using legal player observation only.

Binding dataset:
- all V26B consensus trajectories;
- teacher-bank modal complete action is the offline label;
- source/opponent identity is provenance only and never enters runtime features.

Frozen train/holdout split:
- split by CONTROL functional outcome cluster first;
- within clusters, hold out fresh seeds;
- no random-row split.

Model ladder, one-way only:
1. exact deterministic action rule / state machine if action labels are sufficiently invariant;
2. compact tree ensemble if exact rules are insufficient;
3. compact neural policy only if tree held-out action agreement saturates below the viability gate.

Do not skip directly to a neural model.

Required policy coverage before any causal benchmark:
- complete-action top-1 agreement >=80% overall holdout;
- >=70% within every holdout functional cluster;
- market-component agreement >=85%;
- farmer-component agreement >=85%;
- hands-component agreement >=80%;
- no source/rank/SHA/opponent identity feature;
- deterministic inference;
- Kaggle-safe package/runtime.

If coverage gate passes:
- freeze exactly one distilled policy;
- run untouched fresh causal benchmark against the same architectural CONTROL on new seeds;
- no hosted submission before fresh causal PASS.

If coverage gate fails:
- close consensus distillation; move to Route B strategy reassessment.

## Route B — V26B_NO_SOURCE_AGNOSTIC_POLICY_HEADROOM

If and only if binding V26B returns:
`V26B_NO_SOURCE_AGNOSTIC_POLICY_HEADROOM`.

The following branches are CLOSED:
- V47+ALL3 additive options;
- finite shadow-prefix transfer;
- compact opponent-independent interaction controller;
- PrizeSolverV4 heuristic base;
- simple source-agnostic modal teacher policy.

Open exactly one block:

**V27A_COMPETITION_STRATEGY_REASSESSMENT**

V27A must compare three paths without assigning a winner from intuition:

A. **New learned/search architecture**
   - build a genuinely new persistent first-party policy/value/search architecture;
   - may use exact-engine offline teacher/counterfactual data;
   - must not be a heuristic patch to PrizeSolverV4 or ALL3.

B. **Preserve best hosted candidate + publication/paper track**
   - keep the strongest proven hosted package untouched;
   - convert the accumulated causal/negative evidence into publication-quality artifact;
   - continue competition only when a new architecture clears an offline gate.

C. **Competition exit / resource reallocation**
   - quantify remaining prize upside versus compute/time opportunity cost;
   - compare against the user's other active competitions;
   - do not continue Kaggriculture purely because of sunk cost.

V27A evidence must include:
- current hosted standing / submission state;
- remaining competition deadline and prize structure from current Kaggle metadata;
- strongest current public frontier snapshot;
- all closed architecture families V19-V26;
- estimated compute burden of a genuinely new learning/search architecture;
- whether external GPU/CPU is actually necessary.

V27A may recommend continuation only after this evidence is assembled; no new solver implementation begins before that reassessment.

## Route C — V26B_MECHANICS_INVALID

Repair mechanics only and rerun exact same:
- immutable teacher bank;
- immutable opponent snapshot;
- consensus rule;
- seeds 79601..79606;
- both seats;
- frozen gate.

No strategic mutation.

## Submission rule

No V26B outcome directly authorizes a Kaggle submission.
