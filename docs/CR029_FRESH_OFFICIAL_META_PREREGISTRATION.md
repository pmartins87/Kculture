# CR029 — Fresh official-meta calibration preregistration

Date: 2026-09-05

## Why CR029 exists

CR027 and CR028 produced two independently credible challengers to CR024 after the package/harness issues were corrected.

### Indar V1

Exact public package: `indarkarhana/shape-the-shop-work-the-pasture-top-10/versions/1`.

Correct package-aware CR027 rescue result, frozen seeds/opponents:

- mechanical: PASS;
- direct vs CR024: **8/12** W/L score;
- direct mean delta: **+3379.08**;
- paired reactive W/L gain vs CR024: **+2.0**;
- reactive improvements: 2;
- reactive regressions: **0**;
- paired reactive mean delta gain: **+1284.67**;
- decision: `SHORTLIST_FOR_HOSTED_CALIBRATION`.

The earlier Indar failures were harness failures caused by discarding package siblings and then by an invalid wrapper placement before a `__future__` import. They are not counted as strategic evidence.

### CR028 full_recent_top

CR028 Stage A compared a current strong public route and five prefix splices against CR024 with frozen fresh seeds and exact Rayk/Boatlee/Prvsiyan packages.

Only the **complete recent-top route** passed:

- direct vs CR024: **4/8** W/L score;
- direct mean delta: **+3784.5**;
- paired reactive W/L gain vs CR024: **+2.0**;
- reactive improvements: 2;
- reactive regressions: **0**;
- paired reactive mean delta gain: **+2195.38**;
- decision: `SHORTLIST_FOR_FRESH_HOSTED_CALIBRATION`.

All state-incoherent prefix splices failed the frozen gate. This is evidence for preserving the complete coherent policy instead of arbitrarily grafting its opening onto CR024.

## CR029 candidates

The candidate set is frozen before CR029 outcomes:

1. `cr024` — current control.
2. `full_recent_top` — exact 719-action policy from episode `105248818`, seat 0, observed current-engine rating 2645.2715; stream hashes are frozen in `configs/cr029_fresh_official_meta_calibration.json`.
3. `indar_v1` — exact pinned public package above, with archive and `main.py` SHA256 frozen in config.

## Fresh official-meta panel

Source date: **2026-09-05**.

The harness reads the official daily Kaggriculture episode dataset. Episodes are considered in descending manifest `avg_score`, scanning at most the first 30. A scenario is accepted only when:

- the episode has 720 steps and a non-tied terminal winner;
- both 719-action tapes can reproduce the original terminal rewards exactly under the original episode seed and configuration;
- the winning tape SHA256 is unique among already accepted scenarios.

Target: **12 unique exact winner tapes**. Mechanical minimum: **8**.

No team, episode, submission or rating identity is available to any runtime agent. Identity is evaluation metadata only.

For every accepted winner tape, each of the three candidates is tested against it using the original episode seed/configuration in **both candidate seats**. CR024 therefore provides an exactly paired control row for every finalist row.

## Independent fresh pairwise panel

Frozen seeds:

`1735090501, 1735090529, 1735090571, 1735090607, 1735090661, 1735090703`

Before any result is produced, the harness scans every other JSON config in `configs/` and aborts if any of these values were previously used as seeds.

Both seats are run for each seed for:

- `full_recent_top` vs CR024;
- `indar_v1` vs CR024;
- `indar_v1` vs `full_recent_top`.

## Frozen promotion gate

A finalist must satisfy all of:

- mechanically complete CR029 run;
- official-meta paired W/L gain vs CR024 **>= 0**;
- at most **2** official-meta W/L regressions vs CR024;
- fresh 12-game pairwise score vs CR024 **>= 5.0**.

Passing finalists are ranked, in order, by:

1. higher official-meta W/L gain vs CR024;
2. fewer official-meta W/L regressions;
3. higher absolute official-meta W/L score;
4. higher fresh pairwise score vs CR024;
5. higher direct finalist-vs-finalist score;
6. higher official-meta mean delta gain vs CR024.

No threshold rescue is permitted after outcomes are seen.

## What CR029 authorizes

A winner is promoted only to **Kaggle package preflight**. CR029 itself does **not** authorize or make a Kaggle submission.

- no held-out set is touched;
- no automatic submission;
- no identity-aware runtime logic;
- no post-outcome threshold changes.
