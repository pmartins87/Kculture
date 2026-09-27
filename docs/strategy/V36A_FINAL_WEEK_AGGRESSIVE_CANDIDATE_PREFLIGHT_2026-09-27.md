# V36A — Final-Week Aggressive Candidate Preflight — 2026-09-27

Workflow: `36286643137` — SUCCESS.

## Live hosted snapshot

UTC: `2026-09-27T01:50:44Z`.

Current active/latest-two:
1. Barnyard V7 `56593614` — COMPLETE — **740.4**.
2. Kaito V2 `56593613` — COMPLETE — **809.9**.

These are treated as failed hosted transfers. They are not protected by strategy.

Submissions used today (UTC): **2 / 5**.
Remaining today: **3**.

## Exact current public candidates frozen and mechanically validated

### Ahmed V45
- notebook: `ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip`
- exact version: V1
- observed current public score: **2765.5**
- archive SHA-256: `b8c2f5aab88faf2332e45f721ec83e5f9e7bec3d0a995cc0dce318badd884ed0`
- main SHA-256: `2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94`
- mechanical smoke: PASS 4/4

### Tetsutani V23
- notebook: `tetsutani/market-smart-farming-kaggriculture`
- exact version: V23
- observed current public score: **2750.4**
- observed freshness: roughly 7 hours old at discovery
- archive SHA-256: `2b3ada6a797f713a1ebb25149ae307882562f191dead8ba498ca8661f47e3ba2`
- main SHA-256: `1a97f872f4af6658e3fe16f6bca401f9e66ce5a54a1527482d730b68d4011b0b`
- mechanical smoke: PASS 4/4

### Rayk V22
- notebook: `raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta`
- exact version: V22
- observed current public score: **2837.0**
- archive SHA-256: `312e4f02b22bb9587d62ffcb56592883bc539338aad2dcc7fea0f19c4d6cc931`
- main SHA-256: `489f5d197527f107027626cce79d850fd2ca90edd43d94384b849b6511e27bdb`
- mechanical smoke: PASS 4/4

## Final-week policy correction

Do not conserve daily submissions merely to preserve low-performing active slots.

However, do not fire all remaining submissions simultaneously because only the two newest remain active and an immediate third submission would destroy the information value of the first.

Recommended adaptive order if explicitly authorized:
1. **Ahmed V45 first** as the sacrificial transfer probe.
2. **Tetsutani V23 second** as the freshest keeper candidate.
3. **Rayk V22 last** as the highest-current-score keeper.

The exact timing between submissions should be driven by early hosted feedback, not by offline local ranking.

No Kaggle mutation is performed by V36A itself.
