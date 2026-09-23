# V28L — Physical Causal Temporal Localization Protocol

Date: 2026-09-23

Status: **PRE-REGISTERED before V28L outcomes**.

## Trigger

V28J independently returned `V28J_BOUNDED_LEGAL_HISTORY_RISK_PHENOTYPE_NOT_IDENTIFIABLE`, closing simple classifier-based gating on the 384–480 history window.

V28K independently returned `V28K_NO_MIDGAME_WINDOW_WL_HEADROOM`. MARKET and FULL produced zero loss-to-win flips in 384–479. PHYSICAL produced exactly 4 flips across 2 sources and both seats with positive mean score delta, but all flips were concentrated in seed 80401, so it failed the frozen >=2-seed robustness rule.

The only justified causal lead is therefore the physical action domain, but the 384–479 window itself is exhausted. V28L localizes whether robust physical-domain headroom exists **outside** that window. It does not retune V28J or weaken V28K.

## Frozen population and provenance

Use exactly the immutable V28F snapshot and exactly the 66 V28F ALL3 residual-loss contexts. No source reacquisition, no source dropping, no target reselection. BASE must reproduce exact V28F terminal score and margin for every context.

Opponent source/rank/SHA may be retained only as offline forensic metadata and never as a runtime policy feature.

## Frozen intervention

Use the same V28K physical upper-bound construction: ALL3 remains the candidate policy, while only `farmer` + `hands` are replaced by the immutable opponent/teacher action inside the selected time window. MARKET remains ALL3.

Frozen non-overlapping windows outside the exhausted V28K interval:
- EARLY: 0–191;
- PRE_MID: 192–383;
- LATE: 480–719.

Also run BASE once per context for exact replay parity. No overlapping window sweep, boundary search, or post-outcome resizing is allowed.

## Frozen metrics and gate

For each window report loss-to-win flips, loss-to-tie flips, mean/median margin delta, mean score delta, flip sources, flip seeds and flip seats.

A window has robust physical W/L headroom iff all are true:
- loss-to-win flips >= 4;
- flip sources >= 2;
- flip seeds >= 2;
- mean score delta > 0.

If multiple windows pass, select the one with the largest loss-to-win flips; tie-break by larger mean score delta, then larger mean margin delta, then chronological order EARLY, PRE_MID, LATE. These tie-breaks are frozen before outcomes.

## Frozen decisions

- any window passes => `V28L_PHYSICAL_TEMPORAL_HEADROOM_LOCALIZED`; freeze the selected window and route to first-party legal physical-action mechanism translation inside that window only.
- no window passes => `V28L_NO_ROBUST_PHYSICAL_TEMPORAL_HEADROOM`; close opponent-action physical imitation as a practical rescue path for the V28F hard core and return to broader first-party mechanism discovery/final competition strategy rather than weakening thresholds.

Mechanical failure => repair mechanics only and rerun unchanged.

No Kaggle submission, deletion, or reordering is authorized.