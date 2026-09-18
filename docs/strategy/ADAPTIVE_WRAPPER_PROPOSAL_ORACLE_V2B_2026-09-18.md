# Adaptive Wrapper Proposal Oracle V2b — 2026-09-18

## Why V2b exists

V2 workflow run `35310579248` is mechanically invalid and contains no strategic data.
All five proposal generators were downloaded and SHA-verified, but V39 has no packaged
root `main.py`; its notebook-source fallback requires Kaggle authentication. V2 was
deliberately run without a private token, so acquisition stopped before any episode.

Do not interpret V2 run 1 as PASS or FAIL.

## Frozen change from V2

Everything from
`docs/strategy/ADAPTIVE_WRAPPER_PROPOSAL_ORACLE_V2_2026-09-18.md`
remains frozen except the second opponent block:

- block 1: exact V47 mirror, unchanged;
- block 2: exact packaged V48 Clear-the-Queue, replacing V39 for this public/no-secret
  gate.

V48 exact source SHA:
`4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96`.

V48 already passed acquisition/hash verification in invalid V2 run 1 and shares the
modern programme bank while implementing a different queue-cleanup layer. The same V48
bytes may simultaneously act as a shadow proposal generator and as an independent
opponent instance; module state must be fresh per role/episode.

Seeds remain `63001, 63002`, both seats. Proposal generators, event selection, action
compatibility rules, thresholds and frozen outcome names are unchanged.

## Interpretation limitation

V2b is a **modern-lineage headroom gate**. A PASS justifies learning the proposal
selector, but promotion beyond research still requires later transfer to an independent
legacy/additional lineage. A FAIL closes one-turn wrapper-proposal switching on the
modern panel; it does not retroactively create a V39 result.
