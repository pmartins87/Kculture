# Public meta continuation snapshot — 2026-08-26

## Purpose

Record current public evidence about the Kaggriculture high-rating meta while Kculture's development failure atlas is running. This file is research/hypothesis context, not imported policy code and not promotion evidence.

## Current public benchmark pages

### Kaito Fukami — v27 Midgame Meta Reset

Public notebook:
`https://www.kaggle.com/code/kaitofukami/25-27-strict-future-v27-midgame-meta-reset`

Current page snapshot observed 2026-08-26:

- Public Score: **3090.1**
- Best Score: **3090.1 V4**
- page displays Apache-2.0 notebook license

The public notebook's research text reports:

- 26/30 sampled Top-30 teams share a 1-COW / 4-SHEEP core;
- 14/30 used the HIRE4 basin and 12/30 HIRE5;
- v27 retains the same low-entropy HIRE4 opening and replaces the stale continuation;
- first market difference from the prior route appears around step 161;
- first farmer/hands difference around step 170;
- one coherent 719-step route is used in both seats;
- relative to the prior route, the selected continuation planned less wheat purchase (360 vs 380), more milk sales (241 vs 218), and slightly fewer fertilizer sales (235 vs 245);
- the sparse market layer only reorders already-existing SELL slots and does not create/delete/resize ordinary SELLs;
- reported strict-future counterfactual was 25/27, explicitly not an official Public-LB score.

The notebook identifies exact production `main.py` SHA-256:
`f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`
and size 20,813 bytes.

### Rayk Kretzschmar — Rank Your Agent

Public page:
`https://www.kaggle.com/code/raykkretzschmar/kaggriculture-rank-your-agent`

Observed public best-score snapshot: **2990.4 V11**.

### Andrey Naymushin — Breaking the Tie

Public page:
`https://www.kaggle.com/code/andrewsokolovsky/kaggriculture-breaking-the-tie`

Observed public best-score snapshot: **2915.2 V12**; page displays Apache-2.0.

## License/provenance caution on exact Kaito v27 artifact

A separate public research repository (`sota1111/kaggriculture-gpt`, commit `cfbe024a...`) records an authenticated 2026-08-22 acquisition of the exact Kaito v27 output with the same `main.py` SHA-256 but marked the downloaded metadata/body license as unspecified and therefore prohibited redistribution fail-closed at that time.

Because the current Kaggle notebook page now displays Apache-2.0 while that earlier exact-output acquisition ledger recorded no license declaration, Kculture will **not import or redistribute the exact v27 bytes until authenticated acquisition independently verifies the version/license boundary**.

The public research description and mechanics remain usable as hypothesis context.

## Strategic implication for Kculture

The high-rating public meta suggests the current edge has moved away from simply choosing a Day-0 opening. The reported Top-30 opening distribution is highly concentrated, while Kaito v27's largest improvement came from replacing the continuation after roughly step 161.

This changes the priority order for Kculture:

1. finish the 16-seed development failure atlas for the validated COK-based candidate;
2. identify where its remaining losses occur and whether they cluster by midgame economy/continuation rather than terminal liquidation;
3. treat a **coherent midgame continuation architecture** as the next high-value research family;
4. avoid a naive late switch between independent full policies, because Kculture's prefix-divergence experiment already showed COK and Seyamalam commit different capital at state index 1;
5. prefer an independently designed continuation that is internally compatible with its opening/state assumptions;
6. acquire exact newer public benchmark bytes only after authenticated license/provenance verification.

## Claim boundary

Dynamic public scores are target signals, not strength proofs against Kculture. No claim is made that a 3090 public notebook would achieve the same score today or that Kculture is near that rating before hosted ladder evidence exists.
