# Kculture — exact continuation (2026-09-11)

Read STATUS.md, ROADMAP.md, docs/SUBMISSION_LEDGER.md, the CR080 protocol and result
bundle first. Working branch is fix/kaggle-parity-v1; main points to it.

1. Check GitHub run **34655496708** (CR080 independent confirmation). Download
   artifact `cr080-confirmation-gate-v1` after completion; inspect every required
   H2H for errors/non-DONE/missing rows, not just workflow SUCCESS.
2. PASS -> prepare one hosted probe with exact archive
   `CR080_MENGFEI_DAILY_ROUTE_BRIDGE_V1.tar.gz`, SHA256
   `cc9f30b833b292d3f735d6c821f3844e3fd3a0a3d840500616bb0369132a7a2d`.
   It is in package freeze run 34655053162 / artifact 10284414571.
   Replacing older active CR070A 56091951 preserves CR071M 56124705.
   Do not delay for optional tests. No automatic Kaggle submission is in workflow.
3. FAIL -> close CR080 daily-route implementation, diagnose the failed worlds
   using current API replays and exact traces, then choose a materially different
   mechanism. No threshold/route-weight rescue on these seeds.
4. Pending/queued -> check job progress and wait only to completion or an explicit
   60-minute user checkpoint. Missing output or execution errors are not FAIL
   evidence about strategy; resolve the concrete mechanical cause first.

CR080 discovery: valid 10W/6L across 8 seeds, 5W/3L each seat; frozen gate 0.625.
Original loader run 0-16 is INVALID: __file__ NameError was being coerced to PASS
by legacy harness. The fixed harness now rejects returned exceptions/non-dicts;
all contract tests and the valid screen passed. No policy retuning occurred.

CR079 already closed, run 34562284953, composite 0.28566 vs baseline 0.37223.
CR078 already closed. Do not rebuild either from older chat instructions.

Authenticated API source is GitHub Actions secret KAGGLE_API_TOKEN; never ask the
user for a screenshot when the API exposes the data. Current snapshot run
34655053172: CR071M 1728.2 / 296 episodes; latest 32 = 7-23-2. CR070A 1717.1.
Main scheduled collector repaired in c47d62dd to resolve current submissions.

Confirm current active slots through the API before any actual hosted submission.
Always tell the user what to do next and give a defined waiting endpoint.
