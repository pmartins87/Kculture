# ALL3 V19D O-TM1 Hosted Package & Parity Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED BEFORE V19C RESULT.

Activate only if:
`V19C_CONSENSUS_FRESH_PASS`.

## Candidate

Exact:
- pinned public V47 base;
- O-RW1;
- O-TW1;
- O-LQ2;
- frozen O-TM1 P2 consensus schedule.

Binding V19A schedule SHA256:
`c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22`.

No schedule edits are permitted.

## Package form

Build one deterministic hosted package:
`KCULTURE_V47_ALL3_TM1_V1.tar.gz`.

Requirements:
- exact pinned V47 base main SHA;
- embed the frozen V19A schedule directly into standalone `main.py`;
- final hosted entrypoint is the TM1 wrapper;
- no external runtime file dependency;
- include attribution/provenance receipt;
- deterministic tar.gz timestamps/metadata;
- no opponent identity/rating/seed/seat/context/future/outcome feature.

## Reference semantics

Package must be exactly action-equivalent to:

1. pinned V47 public base;
2. first-party `apply_option_host(... use_rw=True,use_tw=True,use_lq2=True)`;
3. frozen `schedule_action` from O-TM1.

## Mechanical package parity

Fresh parity seeds:
- 78701;
- 78702.

Offline parity opponents:
- V47 mirror;
- V48;
- tactical-memory public agent.

Both seats.

Expected:
- 3 opponents × 2 seeds × 2 seats = 12 paired reference/package contexts.

PASS requires:
- candidate entrypoint exact expected name;
- exact action trace parity for every call;
- exact final reward parity;
- 12/12 pairs;
- zero failures.

Decision:
- `V19D_PACKAGE_PARITY_PASS`;
- `V19D_PACKAGE_PARITY_FAIL`.

## Promotion

Only `V19D_PACKAGE_PARITY_PASS` may authorize one hosted Kaggle submission of the frozen package.

The hosted submission is for external validation/measurement only. No post-hoc package mutation is allowed after observing hosted performance; any later change is a new candidate/version.

No submission is performed by this protocol itself.
