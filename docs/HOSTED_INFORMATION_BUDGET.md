# Hosted submission information budget — Kculture

Date adopted: 2026-08-27

## Principle

When the Kaggriculture UI exposes a daily submission allowance, that allowance is a **perishable information budget**. Unused daily opportunities do not accumulate value for the project. Because Kculture has demonstrated a large local-to-hosted calibration mismatch, the ladder must be used as part of the experimental system rather than only as a final promotion stage.

The user currently reports a five-submission-per-day allowance in the competition UI. Treat that as current operational information, not as a permanent rules invariant; re-check if the UI/rules change.

## Calibration submission != promotion

A hosted submission may be worthwhile even when it is not locally superior, provided it answers an important unresolved question about the real field. Its hosted rating/episodes are evidence, not a declaration that it replaces the champion.

## Eligibility for an information submission

A candidate should normally satisfy all of:

1. mechanically valid end-to-end;
2. self-contained package with parity/smoke evidence;
3. materially different strategic hypothesis or a clean A/B isolation of one important mechanism;
4. hosted result would resolve a specific uncertainty that local tests cannot resolve well;
5. no known catastrophic bug or rule violation;
6. provenance/hash recorded before upload.

A local W/L PASS is **not required** for a calibration submission when the explicit purpose is to measure a known local/hosted mismatch. Conversely, a locally strong candidate can still be a poor use of a hosted slot if it is behaviorally redundant with an existing submission.

## Daily operating rule

Prefer a small portfolio of high-information submissions rather than zero submissions or indiscriminate uploads. When suitable candidates exist, aim to use available daily capacity on orthogonal questions such as:

- architecture A/B tests;
- opponent-aware vs static policy;
- order-sequence or shared-market response variants;
- production/allocation architecture changes;
- package/environment calibration anchors.

Do not upload merely to consume quota. The test question must be written down first.

## Evidence collection

For every hosted calibration submission record:

- submission ID;
- exact archive SHA-256;
- upload time;
- intended question;
- score snapshots over time;
- episode IDs/replays when available;
- opponent/matchup failure patterns;
- decision after sufficient evidence.

Episode-level forensics has priority over interpreting a single early rating number.

## Current implication

R4B and KEXP-050 prove that local public-agent results can be badly misleading. CR-008/CR-011 form a potentially high-information A/B pair because they share the same opponent-prediction layer and differ primarily in adaptive market-order placement. CR-011 is not a local promotion candidate after CR-013, but either member may still be worth a hosted calibration slot if package parity is established and the explicit goal is to measure whether shared-market response mechanics transfer to the live field.
