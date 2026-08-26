# KEXP-20260826-015 — R4D default-route counterfactual

Status: **COMPLETE — both universal overrides rejected; contextual selector required**

## Motivation

KEXP-014 isolated the final 8C/6S production regime as the strongest modern-panel weakness of frozen `R4B-market-only-validated-v1`: 19 baseline exposure games, 12-7, mean terminal delta +1143.0 and mean 672→terminal swing -3820.421.

Frozen COK V8 source establishes that final 8C/6S is the default route after three visible shops when the first-three prefix contains neither `YARN_STORE` nor an early milk-support shop.

## Candidates

1. **R4D-A / default→10C4S** — after three shops are visible, replace only a final original `8c6s_3q` decision with `10c4s_3q`.
2. **R4D-B / default→6C8S** — same trigger, substitute `6c8s_3q`.

Both retain every other frozen COK V8 decision/controller plus validated R4B terminal market completeness.

Candidate blobs:

- R4D-A `a125e878ef262141cd2fd452a9f4edab42dfbae5`;
- R4D-B `34b66bc18471ffbb7d35f24f2ac39451bc8cb851`.

## Frozen protocol

- development only;
- all 16 frozen development seeds;
- both seats;
- Kaito V27 V4, Rayk V11, Andrew V12;
- 96 episodes per candidate;
- exact KEXP-014 baseline comparator;
- no validation or held-out use.

Actions run **32966913616** — SUCCESS, all six matrix jobs clean.

Artifacts:

- 10C4S/Kaito `9606186992`, ZIP SHA-256 `fcc5960f050b825ff695b83ef63a1f674831b566948f1be6d175ec60ac4621c7`;
- 10C4S/Rayk `9606229777`, ZIP SHA-256 `009bae2af2f2d68b44ec1dc4c21ff23d3702d7f60980de22f97c6480f556da6e`;
- 10C4S/Andrew `9606202564`, ZIP SHA-256 `2a95841d348451285da6f439dc77773da831d95e8922ce142874e2636a6ffe59`;
- 6C8S/Kaito `9606162584`, ZIP SHA-256 `1389f6c8854a8634ab2ab372dfa1e6bea4bbb653a3cf0465a4f1cfffa69295b6`;
- 6C8S/Rayk `9606222343`, ZIP SHA-256 `ed39f2e585608ba94fb354e40037773985d1e711ad1620637d1cb3c2c79ba4a8`;
- 6C8S/Andrew `9606174328`, ZIP SHA-256 `42f63f06f7f0ca5725a5e1f3ddc0070ac8eaa20e638939f5cb69180dc38a99a8`.

## Aggregate results

| Candidate | W-L-T | Score | Mean terminal delta | Mean 672→terminal swing |
|---|---:|---:|---:|---:|
| frozen R4B baseline | **81-15-0** | **0.84375** | +5,720.500 | -2,226.240 |
| default→10C4S | **81-15-0** | **0.84375** | **+5,908.542** | -2,216.198 |
| default→6C8S | 78-18-0 | 0.81250 | +5,700.260 | -1,740.208 |

R4D-B fails immediately on competition-aligned W/L score.

R4D-A raises mean money margin but does **not** improve W/L score. The reason is a clean cross-family swap rather than noise.

## Baseline-defined 8C/6S exposure set

| Candidate | W-L | Mean terminal delta |
|---|---:|---:|
| baseline 8C/6S | **12-7** | +1,143.000 |
| default→10C4S | **12-7** | **+2,093.105** |
| default→6C8S | 9-10 | +1,040.737 |

The 10C4S override changes outcome in exactly four baseline exposure rows, all on development seed `163219477`:

- Rayk V11 seat 0: baseline LOSS -1188 → 10C4S WIN +1833;
- Rayk V11 seat 1: baseline LOSS -1188 → 10C4S WIN +1833;
- Andrew V12 seat 0: baseline WIN +392 → 10C4S LOSS -2449;
- Andrew V12 seat 1: baseline WIN +204 → 10C4S LOSS -4077.

Thus the two extra Rayk wins are exactly cancelled by two Andrew regressions. Kaito preserves its 5-3 result while all eight Kaito default-exposure margins improve under 10C4S, but no loss flips.

Importantly, paired comparison confirms the mutation is surgically scoped: outside the baseline-defined default 8C/6S exposure rows, terminal margins are unchanged. The result is therefore a genuine route-choice interaction rather than accidental policy drift.

## Decision

**Reject both fixed overrides for promotion.**

The evidence establishes a stronger conclusion than either universal reroute:

- route choice matters materially;
- 10C4S is often economically superior in the default regime;
- the correct choice depends on the opponent's **public in-game state**, because the same exogenous default shop regime can favor 10C4S against Rayk/Kaito yet favor baseline 8C6S against Andrew;
- opponent identity and seed identity are forbidden and unnecessary.

This mirrors the successful design principle already used by COK V8 for its third-Yarn correction: combine the shop-prefix trigger with a small public-state divergence rule rather than blanket rerouting.

## Next experiment

KEXP-016 must inspect legal public state at the exact third-shop boundary for the baseline default-route exposure corpus, including:

- first-three shop prefix;
- both public farm production layouts;
- COK-style layout L1 distance;
- public money/labor/tile counts;
- shared market/town state.

Join those features to the paired route counterfactual utility above and search only for a **small interpretable public-state rule**. Any resulting contextual candidate must then return to the full 16-seed × both-seat × three-family development panel before validation is opened.

## Leakage policy

- development: open;
- validation: still sealed for changed R4D code;
- held-out: remains sealed 32/32.
