# CR024 — R4B/COK internal-state warming note

Recorded while the preregistered CR024A Stage-B run was still in progress. This note does **not** alter CR024A or its frozen Stage-B gate.

## Finding

The pinned COK V8 / R4B parent is stateful. In particular, the upstream agent maintains per-seat internal structures including `_META_STATE` and `_ACTION_CACHE`. The COK `agent()` updates meta state on each call, including clone-profile evidence at steps 4, 24, and multiples of 24 thereafter. Several market-control paths depend on accumulated `clone_confidence` and other remembered market state.

The frozen CR024A research implementation deliberately executes the public `top19` tape until the one-time guard at clock 192. It keeps CR008's own 24-turn public-feature history warm, but it does **not** call the R4B/COK base agent during clocks 0..191. Therefore, if the guard fires, the R4B/COK internal meta state starts cold at the switch point.

## Consequence

The current Stage-B run evaluates exactly that cold-base fallback policy. Its result remains valid for that candidate and must not be changed after seeing the gate.

If CR024A passes, any submission package authorized from this branch must reproduce the same cold-base semantics exactly. Package parity must compare complete action traces against the research implementation.

## Successor hypothesis: warm-base fallback

A distinct successor may call the frozen CR008/R4B path every turn before clock 192 **only to update its internal state**, discarding its proposed action while the top19 tape remains active. If the guard fires, the switch would then enter a fully warmed CR008/R4B state.

This is a materially different strategy and requires its own development/validation path. It must never be silently substituted into CR024A after the current Stage-B result is known.

Suggested evaluation order if pursued:

1. implement `CR024A-WARM` separately;
2. compare cold vs warm on already-open Stage-A seeds first;
3. if a meaningful causal difference exists, freeze the warm policy before exposing any fresh validation block;
4. retain the same no-identity/no-seed runtime constraints.

## Submission policy

Do not submit cold and warm variants merely as calibration repeats. A warm successor becomes hosted-submission eligible only if it demonstrates materially different behavior and passes its own mechanical/evaluation gate.
