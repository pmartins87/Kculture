# ALL3 V25A Outcome Router / V25B Architecture Protocol — 2026-09-21

## Status

PRE-REGISTERED while binding V25A workflow `35645830010` is still running, before reading any V25A horizon outcome.

This document freezes the next branch so the V25A result cannot be followed by post-hoc architecture choice.

## Binding V25A

Protocol:
`docs/strategy/ALL3_V25A_SHADOW_PREFIX_STATE_BASIN_PROTOCOL_2026-09-21.md`.

Frozen horizons:
`[0,4,8,16,32,64,128,256,720]`.

Frozen selector:
smallest finite horizon passing the V25A multi-source / multi-cluster / multi-seed W/L gate.

## Route A — EARLY_STATE_BASIN_HEADROOM

Triggered only by:
`V25A_EARLY_STATE_BASIN_HEADROOM`.

Selected horizon must be exactly the binding V25A minimum passing H in:
`[4,8,16,32]`.

Open exactly one V25B family:

**V25B_EARLY_BASIN_POLICY_DISTILLATION**

Goal:
replace the teacher prefix with one identity-free first-party opening policy covering turns `0..H-1`.

Restrictions:
- no per-source branch;
- no source/rank/SHA/cluster runtime feature;
- no teacher call at runtime;
- no new horizon search;
- no shorter/longer H adjustment;
- legal player observation only;
- preserve exact ALL3 after turn H.

Distillation priority:
1. deterministic invariant action transformation;
2. compact state machine over legal observations;
3. decision tree only if needed, max depth 4, min leaf 8, balanced, fixed seed 20260921.

Any distilled candidate must be frozen before fresh causal validation.

## Route B — LONG_STATE_BASIN_HEADROOM

Triggered only by:
`V25A_LONG_STATE_BASIN_HEADROOM`.

Selected H must be exactly the binding minimum passing H in:
`[64,128,256]`.

Open exactly one V25B family:

**V25B_LONG_BASIN_POLICY_DISTILLATION**

Interpretation:
the gain requires sustained trajectory control, so this is not an additive micro-option.

Restrictions:
- same identity-free rules as Route A;
- no attempt to compress to <=32 turns after seeing the result;
- no MARKET_ONLY / PHYSICAL_ONLY revival;
- no per-source policy.

Architecture:
- one first-party finite-state policy for the selected prefix;
- ALL3 resumes exactly at H;
- teacher is offline label only.

Fresh causal validation is mandatory.

## Route C — PERSISTENT_POLICY_REQUIRED

Triggered only by:
`V25A_PERSISTENT_POLICY_REQUIRED`.

This closes the additive-option architecture around exact V47+ALL3.

Do not:
- add V26 micro-options to ALL3;
- retune old V5-V24 thresholds;
- search more prefix horizons;
- use source identity to route;
- turn FULL_SHADOW into a hosted candidate.

Open exactly one architecture benchmark:

**V26A_FIRST_PARTY_BASE_ARCHITECTURE_BENCHMARK**

Its purpose is to choose whether the next competitive path is:

A. materially different first-party base architecture;
B. reconstruct a general teacher-derived policy from legal state;
C. stop solver expansion and preserve the best proven candidate / publication track.

V26A must compare architectures on fresh seeds and current-frontier opponents, with exact snapshotting as in V23.

No architecture may be chosen by public leaderboard score alone.

## Route D — NO_REPRODUCIBLE_SHADOW_HEADROOM

Triggered only by:
`V25A_NO_REPRODUCIBLE_SHADOW_HEADROOM`.

Treat this as semantic mismatch, not strategic evidence.

Action:
- audit V25A H=720 implementation against V23B FULL_SHADOW;
- do not open V25B/V26 until parity is restored.

## Route E — MECHANICS_INVALID

Triggered only by:
`V25A_MECHANICS_INVALID`.

Action:
- repair mechanics only;
- rerun exact same 93 contexts, 9 horizons, snapshot and gate;
- no strategic mutation.

## Promotion rule

No V25A outcome directly authorizes a Kaggle submission.

Any first-party candidate produced from Route A/B must pass:
1. exact local mechanical parity;
2. frozen causal test;
3. untouched fresh multi-seed validation;
4. hosted-package reproducibility;
before submission can even be considered.

## Immediate rule

When V25A completes, apply exactly one route above. No manual tie-breaking.
