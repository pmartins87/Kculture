# CR-008 — High-confidence identity-free adaptive front-run

Status: **FROZEN / PRE-STRATEGY-RESULT**

## Question

Do the high-confidence opponent forecasts proved in CR-004/005/007 improve an actual agent causally when converted into a minimal market best response?

## Frozen candidate

Corrected deployable candidate: `candidates/cr008_adaptive_frontrun.py` blob `8e1c26202c3101c19668bf61edf2ae51d4329d5d`.

Frozen base: `candidates/r4b_ablation_market_only.py` blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

Frozen pure model: `models/cr007_pure_models.json` blob `d4b29e753e2328ac43503f8daa655cc63abdd336`, file SHA-256 `6f12e86d0b19c5ba39c2ab4131e186ea14b49f42cc33b33a2ad895fab55783bb`.

Adaptive behavior is deliberately narrow:

- use only public opponent state; never name/team/submission identity;
- retain 24-turn public history inside the episode;
- CARROT trigger threshold 0.90;
- STRAWBERRY trigger threshold 0.85;
- if triggered and current own shed stock exists, append a same-turn SELL only when the frozen base is not already selling that product and a market slot is free;
- all physical actions and all other market decisions remain frozen R4B behavior.

## Mechanical-null run 1

GitHub Actions run **33099779694** never reached any strategic episode. Candidate/base/model identity checks passed, then the mandatory deployed feature-parity gate failed on exactly the player-1 half of the replay samples: 3000/6000 value mismatches, zero key mismatches. The frozen training encoder treats missing player-1 replay `step` as zero, while the first wrapper reconstructed it from day/hour. Its cache clock reconstruction was also 24 turns low because Kaggriculture `day` is zero-based.

This was corrected **before observing any CR-008 W/L** by separating:

- feature clock: exact CR-004 semantics (`obs.step` or zero when absent);
- memory clock: `obs.step` when available, otherwise `day*24 + hour`.

No seeds, opponents, thresholds, models or strategic response rules changed. Run 1 is therefore recorded as **MECHANICAL_NULL**, not a strategic FAIL.

## Mandatory deployability gates

Before interpreting W/L:

1. exported pure-tree SHA must match frozen SHA;
2. pure-tree probabilities must match sklearn CR-007 to max abs error <= 1e-12 on the Aug-26 temporal test;
3. trigger decisions must agree 100%;
4. deployed feature encoder must match frozen CR-004 feature vectors exactly on >=1000 official Aug-26 states;
5. zero environment/action errors.

Any failure is mechanical and blocks strategy interpretation.

## Fresh exploratory seeds

`configs/cr008_fresh_exploratory_seeds_v1.json` blob `01b29fb4e19cba185b7d99a37ac13ee4715de574`.

12 seeds generated from independent master seed `2026082708`, explicitly excluding development, validation and held-out partitions. Validation/held-out remain untouched.

## Frozen current-meta field

Exact public notebook versions, package `main.py` extracted from the submission archive:

- Kaito Sparse V13 — `kaitofukami/103-128-fresh-public-v43-sparse-shop-hybrid/versions/13` (snapshot score 2882.0);
- Prvsiyan Frontier V10 — `prvsiyan/kaggriculture-frontier-the-soil-remembers-rain/versions/10` (2610.2);
- Tactical Memory V1 — `web3cainiao/kaggriculture-v21-tactical-memory/versions/1` (2491.7);
- Andrew V11 — `andrewsokolovsky/kaggriculture/versions/11` (2441.2).

For each field opponent, CR-008 and R4B play the identical 12 seeds from both seats: 96 episodes per policy. The primary analysis is paired by `(opponent, seed, seat)`.

A direct CR-008 vs R4B exploratory duel on the same seeds is recorded as secondary evidence.

## Frozen causal gate

`ADAPTIVE_CAUSAL_FIELD_PASS` requires:

- complete paired coverage and zero errors;
- positive mean CR-008 minus R4B **own terminal reward** over all paired field games;
- positive mean improvement in relative money delta;
- positive mean own-reward effect in at least 2 of 4 opponent families;
- aggregate field score-rate regression no worse than -0.02 versus R4B;
- no single opponent-family score-rate regression worse than -0.08.

The direct R4B duel is diagnostic and does not override the paired current-meta gate.

A PASS proves only that this bounded adaptation layer adds causal value over R4B on the frozen exploratory field. It does **not** establish prize readiness or authorize a hosted submission by itself. A later broader/current-meta replication is required.
