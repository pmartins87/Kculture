# KEXP-20260826-014 — R4 late-lifecycle full-panel diagnostic

Status: **COMPLETE — generic weed/lifecycle patch rejected; route-selector lead promoted**

## Purpose

Test whether the loss-focused late crop-lifecycle signal from KEXP-013 generalizes across wins and losses before mutating policy. Diagnostic only; development seeds only.

## Frozen candidate

`R4B-market-only-validated-v1`

- path: `candidates/r4b_ablation_market_only.py`
- Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- hosted package remains immutable.

## Exact panel

- `kaggle-environments==1.32.7`;
- exact 16-seed development partition;
- both seats;
- Kaito V27 V4, SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`;
- Rayk V11, SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`;
- Andrew V12, SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5`;
- 96 total episodes;
- zero validation seeds;
- zero held-out seeds.

Actions run: **32931921583** — SUCCESS.

Artifacts:

- Kaito V27: artifact `9593617801`, ZIP SHA-256 `0c74411cc73a4e5c42e60a4d1104ee7206e7eaaf96b95d0635c497f55ef0e61c`;
- Rayk V11: artifact `9593617367`, ZIP SHA-256 `e77fb0b89064b8c25b4e87c219773a68ffedc20e97933b647a91ab454b2202ba`;
- Andrew V12: artifact `9593614809`, ZIP SHA-256 `cc8a00bdcfa999a5c6bf1b142614e687c14b0391260c8c679e1fb82ffd5db814`.

## Exact outcome

| Opponent | W-L-T | Score | Mean terminal delta | Mean 672→terminal swing |
|---|---:|---:|---:|---:|
| Kaito V27 | 25-7-0 | 0.78125 | +4,396.84375 | -2,565.84375 |
| Rayk V11 | 30-2-0 | 0.93750 | +7,477.21875 | -2,165.59375 |
| Andrew V12 | 26-6-0 | 0.81250 | +5,287.43750 | -1,947.28125 |
| **Combined** | **81-15-0** | **0.84375** | **+5,720.5** | **-2,226.2396** |

The late-collapse phenomenon is real, but the predeclared generic crop-lifecycle/weed explanation did **not** generalize in the required direction. Losses did not consistently have more weeds and less productive acreage than wins. A generic weed-cleanup mutation is therefore rejected.

## Stronger structural result: production-route split

The candidate checkpoint at step 672 exposed a much cleaner cross-family separator:

| Production regime | Games | W-L | Score | Mean terminal delta | Mean 672→terminal swing |
|---|---:|---:|---:|---:|---:|
| 6C/12S | 24 | 22-2 | 0.91667 | +8,174.333 | -2,120.875 |
| 10C/4S | 51 | 45-6 | 0.88235 | +6,301.647 | -1,718.686 |
| **8C/6S** | **19** | **12-7** | **0.63158** | **+1,143.000** | **-3,820.421** |
| 9C/4S observed recovery state | 2 | 2-0 | 1.00000 | +4,941.5 | descriptive |

The weak 8C/6S regime reproduced across all three modern families:

- Kaito: 5-3, mean delta +630.625, late swing -4,367.625;
- Rayk: 4-2, mean delta +2,635.167, late swing -4,250.0;
- Andrew: 3-2, mean delta +172.2, late swing -2,429.4.

The baseline-defined 8C/6S exposures occur primarily on development seeds `150614441`, `1369296235`, `393297156`, and `163219477`, in both-seat combinations depending on opponent. These seed identities are used only to audit paired outcomes; no policy may inspect seed or opponent identity.

## Source-level interpretation

Frozen COK V8 route logic establishes that final 8C/6S is the **default no-Yarn/no-milk-support regime** after the first three public shop unlocks:

- first Yarn → 6C/12S;
- Yarn in first two → 6C/12S;
- Yarn in first three → 6C/8S, with V8's milk-support/distance override possibly promoting to 10C/4S;
- no Yarn + early milk support → 10C/4S;
- otherwise → **8C/6S**.

COK V8 already contains bounded weed replay and passive-weed repair controllers. A separate probe of Kaito's recent public weed-slip-recovery agent did not reveal a stronger generic weed mechanism worth copying.

## Disposition

1. **Reject** generic late weed cleanup as R4D.
2. **Promote** the default 8C/6S route selector as the next causal target.
3. Run KEXP-015 fixed-route counterfactuals on development only:
   - default 8C/6S → 10C/4S;
   - default 8C/6S → 6C/8S.
4. If neither universal override passes, build a contextual selector from legal public state rather than broad rerouting.
5. Validation remains sealed for changed code; held-out remains sealed.
