# V27B — Legal-history reconstructibility protocol

Date: 2026-09-21

## Trigger
Binding V27A workflow `35665757174` returned `V27A_HISTORY_AWARE_DISTILLATION_REQUIRED` with 1080/1080 comparisons, zero failures, complete-action fresh-state parity 0.9222222, market 0.9296296, farmer 1.0, hands 0.9925926, minimum checkpoint parity 0.6666667 and minimum source parity 0.8666667.

This protocol is frozen before V27B outcome inspection.

## Question
Can the rank-1 teacher's hidden episode state be reconstructed from a bounded, legal history of observations, without opponent identity, rank, SHA, hidden seed, EpisodeId, future state, private opponent state, or teacher code at candidate runtime?

## Teacher and population
Use the immutable V26A snapshot only. Teacher is rank-1 `ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`, SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`. Opponents are all 12 immutable V26A representatives. Fresh seeds `79801..79803`, both seats.

## Frozen checkpoints and horizons
Checkpoints: `0,1,2,3,4,8,16,32,64,128,256,384,512,640,718`.

History horizons: `0,1,2,4,8,16,32,64,128,256,512,FULL` prior legal observations. For each checkpoint, run the ongoing teacher normally. Independently instantiate a clean teacher, replay only the selected suffix of already observed legal observations in chronological order to reconstruct internal state, then evaluate the checkpoint observation. The replayed teacher outputs are discarded and never alter the environment.

`H=0` is current-state-only fresh reconstruction and must remain consistent with V27A within sampling tolerance. `FULL` replays the whole legal observation history from episode start and is the deterministic upper bound.

## Selection gate
For each horizon compute complete-action parity plus MARKET/FARMER/HANDS parity, per-source parity and per-checkpoint parity.

A finite horizon is viable only if all are true:
- complete-action parity >= 0.99;
- MARKET parity >= 0.99;
- FARMER parity >= 0.995;
- HANDS parity >= 0.99;
- minimum source complete-action parity >= 0.95;
- minimum checkpoint complete-action parity >= 0.90.

Select the smallest finite horizon that passes. If no finite horizon passes but FULL complete-action parity >= 0.995, route to full legal-history distillation. If FULL < 0.995, close fast teacher distillation because replayable legal history does not reproduce the teacher reliably enough.

## Frozen decisions
- finite pass => `V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE`;
- no finite pass, FULL pass => `V27B_FULL_LEGAL_HISTORY_DISTILLATION_REQUIRED`;
- FULL fail => `V27B_TEACHER_HISTORY_NOT_RECONSTRUCTIBLE`.

## Next route
A V27B pass authorizes exactly one first-party behavioral distillation gate using the selected legal-history representation. It does not authorize a Kaggle submission. Failure closes fast rank-1 teacher distillation and returns to final-slot/competition strategy.

No Kaggle submission is authorized.