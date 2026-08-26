# Current-meta acquisition — 2026-08-26

## Purpose

Raise the development benchmark ceiling with exact public Kaggle notebook outputs, acquired by immutable notebook version and then hash-pinned before any tournament interpretation.

Discovery Actions run: `32926623429`.

All Kaggle credential environment variables were explicitly blank. Acquisition succeeded through public KaggleHub notebook outputs.

## Rayk V11

Notebook: `raykkretzschmar/kaggriculture-rank-your-agent/versions/11`

Public Kaggle page snapshot associates Best Score **2990.4 with V11**.

Discovery output:

- `main.py`: 36,233 bytes
- SHA-256: `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`
- `submission.tar.gz`: 17,785 bytes
- SHA-256: `99e3ab82275d1d6991553a50c67f7fb3c83c029072dab2e890155b34d34c3cc1`
- discovery artifact ID: `9591736324`
- discovery artifact ZIP SHA-256: `08b7760a84b0fdeb6e2a32bad5162ba561b7778044e0652bbccb54a6c3bdabb8`

License was not independently surfaced in the captured Rayk page metadata. Treat V11 as a **benchmark-only public artifact** unless/until license is separately verified; do not derive or redistribute its source as Kculture code.

## Andrew V12

Notebook: `andrewsokolovsky/kaggriculture-breaking-the-tie/versions/12`

Public Kaggle page snapshot associates Best Score **2915.2 with V12** and displays **Apache-2.0**.

Discovery output:

- `main.py`: 26,585 bytes
- SHA-256: `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`
- `submission.tar.gz`: 13,994 bytes
- SHA-256: `5e628cb24738d3999d93cd3e38d755561ecf2f6cdc14da0d9b068df8a50c39cc`
- discovery artifact ID: `9591737956`
- discovery artifact ZIP SHA-256: `a47af3d08b7ee722cc3e3da160cfbdea6a88d0c95ca4412f4712517e78faa3e8`

## Benchmark admission rule

Discovery hashes alone do not create a performance claim. Every tournament job must:

1. request the exact notebook version;
2. verify the exact `main.py` SHA-256 above using `tools/fetch_public_kaggle_notebook.py`;
3. use development seeds only for this frontier screen;
4. compare R4A and frozen R4B on the same 16 seeds and both seats;
5. leave validation and held-out sealed.
