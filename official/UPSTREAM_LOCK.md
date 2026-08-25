# Official upstream lock — Kaggriculture

Frozen on: 2026-08-25

## Package used for local reproduction

- PyPI package: `kaggle-environments==1.32.7`
- Release date: 2026-08-15
- Python requirement: >=3.11
- Wheel SHA256: `2a1bb862ad2d6463080f80f6a766f46d94b53fd57168cfeddb9857fc3dbc4c8f`
- Source tarball SHA256: `4679d757e3677ada652d239679767c678a317c3fabdc58a332a3b6c9566ce1c0`

## Official source snapshot

Repository: `Kaggle/kaggle-environments`

Latest commit touching the advanced Kaggriculture engine at freeze time:

- commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`
- date: 2026-08-15
- message: `Make underused resources situational (#1399)`

Tracked upstream file blobs:

| Upstream path | Blob SHA |
|---|---|
| `kaggle_environments/envs/kaggriculture/kaggriculture.py` | `3c202c7ee921da239356789e266b694635103fc4` |
| `kaggle_environments/envs/kaggriculture/kaggriculture.json` | `b354d06b742fe48402513792253f1a5c29366b20` |
| `kaggle_environments/envs/kaggriculture/README.md` | `03758e5878dd5b050178ba22755c4a81d3e3b829` |

Environment specification version: `0.1.0`.

## Baseline provenance

Root `main.py` is a self-contained port of the official built-in `starter_agent` from the frozen engine. The official baseline is a deterministic carrot loop: buy carrot seed, plant on the current tile, water, harvest at carrot max-yield day, and sell carrots from the shed.

The port deliberately contains no strategic improvements. Its purpose is to establish exact legal execution and local↔official parity before Kculture begins optimization.

## Competition-critical defaults captured from the official spec

- 2 agents
- 720 episode steps
- 10×10 board
- 3000 starting money
- 24 turns/day
- 10 market orders/player/turn; extras are silently dropped
- shed capacity 100 non-seed items
- weed spawn probability 0.005 per empty unlocked tile at end-of-day refresh
- town shop unlock interval 3 days
- town shop consumption interval 4 turns
- town-center consumption interval 24 turns
- action timeout 1 second

## Version discipline

Before every promoted ladder submission:

1. check the latest Kaggle competition instructions;
2. check the latest `kaggle-environments` release and advanced Kaggriculture source commit;
3. diff any engine/spec changes against this lock;
4. rerun baseline and champion regression suites if anything changed;
5. record the new upstream version/hash before promotion.

Official upstream is Apache-2.0 licensed. Keep attribution when copying reference code.
