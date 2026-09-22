# V28C — Exact V47 Final-Hedge Submission Result — 2026-09-22

## Authorization

The user explicitly authorized the V28B frozen recommendation: preserve ALL3 and replace O-RW1 with exact V47.

No other candidate was authorized.

## Launch

Workflow: **35739943846**  
Launch commit: **d5d23b2ce570cceac34dd03a90f80f630aebc779**  
Workflow file reused for the one-time authorized action: `.github/workflows/orw1-hosted-ab-submit-v1.yml`.

## Strict preflight

Before mutation, authenticated Kaggle submissions were exactly:
1. ALL3 `56367770`;
2. O-RW1 `56336027`.

Observed at the preflight:
- ALL3 listed publicScore: **1988.8**;
- O-RW1 listed publicScore: **1900.4**;
- UTC submissions already made on 2026-09-22: **0**;
- projected daily count after V28C: **1 / 5**.

Exact V47 recovery passed:
- archive SHA-256: `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- internal `main.py` SHA-256: `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`;
- official Kaggle loader entrypoint: `_y_agent_shopherd`, argc 2.

## Submission

Description:
`PS_V28C_FINAL_HEDGE_EXACT_V47_08E56C43`.

New exact-V47 submission ID:
**`56466970`**.

Initial registered status:
`SubmissionStatus.PENDING`.

## Latest-two verification

Immediately after registration, the newest two submission IDs were exactly:
1. **56466970** — exact V47;
2. **56367770** — ALL3.

O-RW1 `56336027` is no longer in the latest-two active pair.

Therefore the intended final-slot mutation succeeded mechanically:
**ALL3 primary + V47 hedge**.

## Provenance

GitHub Actions artifact:
- ID: `10699168127`;
- digest: `sha256:a24b5f90a57beae66f475ac8f39337c4b0946e330e9d9267871eb0e5af8dd96d`.

The artifact preserves authenticated before/after submission CSVs, preflight JSON, exact hashes, submit timestamps, and V28C result JSON.

## Next action

Read-only monitor submission `56466970` until it leaves PENDING. Do not submit another candidate merely because scoring is pending. After completion, re-audit the current latest-two pair and ratings and update the canonical project sources.
