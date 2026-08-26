# First hosted Kaggriculture submission — R4B market-only validated v1

## Approved agent

`R4B-market-only-validated-v1`

The exact package approved after development, validation, and package-parity gates is:

- archive: `r4b_market_only_v1.tar.gz`
- bytes: `101557`
- SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`
- package parity Actions run: `32919305800`
- package artifact ID: `9589293098`

Do not submit an archive with a different hash under this version name.

## Before submission

The Kaggle account must have accepted the Kaggriculture rules. Official verification command:

```bash
kaggle competitions list --group entered
```

`kaggriculture` must appear.

## CLI submission

Official competition command for a local multi-file agent archive:

```bash
kaggle competitions submit kaggriculture \
  -f r4b_market_only_v1.tar.gz \
  -m "Kculture R4B market-only validated v1"
```

Then:

```bash
kaggle competitions submissions kaggriculture -v
```

Record the submission ref/ID and hosted validation status in `docs/SUBMISSION_LEDGER.md`.

## Repository automation

`.github/workflows/r3-first-hosted-submission.yml` is manual-only and performs the same process after authentication with repository secret `KAGGLE_API_TOKEN`:

1. confirm authenticated Kaggriculture entered status;
2. fetch/hash-check COK V8;
3. verify the frozen Kculture candidate Git blob;
4. rebuild the deterministic archive;
5. verify archive SHA-256 equals the approved value;
6. submit to Kaggriculture;
7. preserve the resulting submission list.

Credentials must never be committed to source control or printed into repository files.

## After submission

1. Wait for Kaggle's self-play Validation Episode status.
2. If valid, record submission ID, rating initialization and eventually episode count/rating.
3. Download hosted logs/replay if behavior differs from local expectations.
4. Reconcile hosted behavior with the exact local package before interpreting ladder rating.
5. Do not replace one of the latest-two tracked slots casually; submission ordering matters.

## Current claim boundary

This agent is locally validated and package-identical to the tested wrapper. It is ready for first hosted ladder measurement, but hosted rating is unknown and no top-10 strength claim is made.

All 32 held-out seeds remain sealed.
