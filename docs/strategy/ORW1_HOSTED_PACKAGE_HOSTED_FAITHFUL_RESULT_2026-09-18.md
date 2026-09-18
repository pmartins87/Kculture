# O-RW1 Hosted-Faithful Package Gate Result — 2026-09-18

## Binding result

Workflow `35372969031`, artifact `10559606269`.

Candidate:
`KCULTURE_V47_ORW1_ONESHOT_V1.tar.gz`

Archive SHA-256:
`997aa273cb64c6acf933f8d719bd358c47d07871f6e42ac056003155499c68c9`

Candidate `main.py` SHA-256:
`39c524b453c2f141758513668cd167e2b30b29cfbbaba3699a9248318f79cf0a`

Wrapper SHA-256:
`9a0e9e1690684ff6f58c15089a1b6d8bda73b8f38fca9d576e61f7cb52e1d32f`

Exact public V47 base:
- archive SHA `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- main SHA `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`;
- hosted entrypoint **`_y_agent_shopherd`**.

Corrected candidate hosted entrypoint:
**`_kc_orw1_entrypoint`**.

## Exact package parity

Fresh seeds:
`66001,66002`.

Opponent blocks:
- exact hosted-faithful V47;
- Tactical Memory.

Both seats.

Results:
- 8 package/reference pairs;
- 16 complete episodes;
- 719 candidate action calls per episode;
- **8/8 exact action parity**;
- **8/8 exact reward parity**;
- failures: **0**.

Package parity JSON SHA:
`e23eee387e8a33711acf4943a30d1df7602f0c8e0d1b28e88ff98b8d8d4a87a7`.

Binding verdict:
**`ORW1_HOSTED_PACKAGE_HOSTED_FAITHFUL_PASS_READY_FOR_CORRECTED_AB`**.

## Important difference from invalid package

The invalid first treatment rebound the pre-existing name `agent`, so Kaggle selected
helper `_kc_orw1_wool` as the final callable.

The corrected package:
- explicitly wraps exact V47 hosted entrypoint `_y_agent_shopherd`;
- defines a unique final callable `_kc_orw1_entrypoint`;
- forbids callable definitions after that entrypoint;
- verifies the staged source through the official Kaggle loader;
- verifies the extracted tar through the same official loader;
- proves action/reward identity to the hosted-faithful runtime reference.

The package is now mechanically eligible for the corrected hosted A/B.
