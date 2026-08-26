# KEXP-20260826-015 — R4D default-route counterfactual

Status: **PREDECLARED / DEVELOPMENT ONLY**

## Motivation

KEXP-20260826-014 completed 96 games (16 development seeds × both seats × Kaito V27, Rayk V11 and Andrew V12) with zero execution errors. The frozen R4B market-only candidate scored 81-15 overall (0.84375), mean terminal delta +5720.5.

The strongest cross-family weakness was the final 8C/6S production regime:

- 19 episodes;
- 12-7 (0.631579);
- mean terminal delta +1143.0;
- mean money swing from step 672 to terminal: -3820.421.

The same regime was weak against all three modern public families. Conversely, 10C/4S was 45-6 and 6C/12S was 22-2 in the same panel.

Source inspection of frozen COK V8 establishes that 8C/6S is the default route after the first three public shop unlocks when those first three contain neither `YARN_STORE` nor a milk-support shop (`PIZZA_SHOP`, `ICE_CREAM_SHOP`, `SMOOTHIE_SHOP`). V8's existing third-Yarn correction does not touch this default regime.

KEXP-014 also falsified the proposed generic late-weed explanation: losses did not show the predicted excess-weed / reduced-productive-acreage signature. Therefore this experiment changes route selection only and leaves the existing weed/recovery controllers intact.

## Candidates

Two deliberately simple counterfactuals are screened before designing a learned/contextual selector:

1. **R4D-A / default→10C4S** — once at least three shops are visible, if frozen COK V8's original selector would still choose `8c6s_3q`, return `10c4s_3q` instead.
2. **R4D-B / default→6C8S** — identical trigger, but return `6c8s_3q`.

Before the third shop is visible, both candidates preserve the base selector exactly. This avoids changing the shared early prefix merely because the provisional selector defaults to 8C/6S while the shop sequence is incomplete.

Both candidates retain the validated R4B terminal market-only liquidation behavior at step 718. No other physical-action, recovery, front-running, terminal, or market-finalization logic is modified.

## Frozen test panel

Development partition only:

- 16 frozen development seeds;
- both seats;
- Kaito V27 V4 (`f48c2116...` source SHA-256);
- Rayk V11 (`adc61ab1...` source SHA-256);
- Andrew V12 (`df4e899a...` source SHA-256).

Each candidate therefore plays 96 modern-panel episodes. The KEXP-014 R4B market-only panel is the frozen baseline comparator.

No validation seed and no held-out seed may be used to choose between R4D-A, R4D-B and the baseline.

## Primary decision rule

Win/loss/tie is primary because the competition rating is driven by match outcome rather than victory margin.

A route counterfactual may advance only if all of the following hold:

1. zero execution errors across the 96-game modern panel;
2. aggregate score rate is **not below** the frozen baseline 0.84375;
3. aggregate mean terminal delta is **not below** +5720.5;
4. in the baseline-defined 8C/6S exposure set, the counterfactual must produce a material improvement rather than merely shift money margin elsewhere; target is at least two additional wins versus the baseline 12-7 exposure result, or an equivalently strong paired outcome supported by the exact seed/seat rows;
5. no opponent family may show a severe new regression that overwhelms the targeted gain.

If neither fixed override passes, the result is still useful: the next candidate must be a contextual default-route selector using public observables rather than a universal reroute.

## Leakage policy

- development: open, permitted for this screen;
- validation: sealed until one exact R4D candidate is frozen;
- held-out: remains sealed.
