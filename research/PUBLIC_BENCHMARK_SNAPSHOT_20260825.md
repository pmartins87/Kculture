# Public Kaggriculture benchmark snapshot — 2026-08-25

This is a discovery snapshot, not a permanent leaderboard ceiling. Kaggle ratings change as submissions and opponents change.

## High-priority public references

| Priority | Public notebook/version | Score snapshot | Why it matters |
| --- | --- | ---: | --- |
| 1 | Kaito Fukami — `25/27 Strict-Future \| v27 Midgame Meta Reset`, V4 | **3090.1** | Highest public reference located in the 2026-08-25 search; Apache-2.0 page license. |
| 2 | Rayk Kretzschmar — `Kaggriculture Rank Your Agent`, V11 best | **2990.4 best** | Independent near-ceiling reference and important architecture/opponent candidate. |
| 3 | Andrew Sokolovsky — `Kaggriculture: Breaking the Tie`, V12 best | **2915.2 best** | Newer independent strong reference; public page is Apache-2.0 and recent build logs explicitly validate same-turn `DROP` credit. |
| 4 | FlexonaFFt — multi-route farming agent, V59 | **2767.3 best** | Earlier strong public multi-route architecture. |

The older Andrew `Kaggriculture` V10 / 2671.3 target has been retired from the acquisition priority list because the newer `Breaking the Tie` V12 snapshot is substantially stronger.

Exact version targets are stored in `configs/kaggle_public_targets.json`.

## Interpretation for Kculture

`R4A-public-base-v1` (COK V8) remains a useful engineering baseline because it is reproducible, attributed, hash-pinned and exposes detailed failure evidence. It is **not** treated as the competitive ceiling. Kculture promotion work should ultimately be challenged against the strongest independently acquired public policies available, especially Kaito V27 V4, Rayk V11 and Andrew Breaking-the-Tie V12.

Public score/rating is discovery metadata, not the development objective. Official Kaggriculture evaluation changes skill rating from win/loss/tie outcomes; terminal coin margin does not change the rating update. Consequently, Kculture's controlled promotion gates keep W/L/T as the primary result and use money delta as diagnostic/tie-break evidence.

## Acquisition constraint

The current Kaggle CLI requires authentication for kernel pulls, including public notebooks. A manual GitHub Actions acquisition workflow is prepared to consume the repository secret `KAGGLE_API_TOKEN`, download exact version specifiers, hash every acquired file, and preserve the artifacts. No Kaggle credential is stored in the repository.

## Evidence discipline

- Public score values above are discovery metadata and may move later.
- Local W/L/T on frozen seeds remains the primary mechanism-development evidence.
- Validation and held-out seed partitions remain closed until a development candidate is frozen.
- Third-party code is not claimed as Kculture authorship; page/artifact license and hashes must be preserved before derivative use.
