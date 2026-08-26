# KEXP-20260826-016 — R4D public-context diagnostic

Status: **COMPLETE / DEVELOPMENT DISCOVERY ONLY**

Actions run: **32968422225** — SUCCESS for Kaito V27, Rayk V11 and Andrew V12.

## Why this experiment exists

KEXP-015 showed that a universal route mutation is too crude.

On the exact 96-game modern development panel:

- frozen R4B baseline: 81-15, score 0.84375, mean +5720.5;
- default→10C/4S: 81-15, score 0.84375, mean +5908.542;
- default→6C/8S: 78-18, score 0.81250, mean +5700.260.

On seed `163219477`, default→10C/4S flips both Rayk losses to wins while simultaneously flipping two Andrew wins to losses. A useful selector therefore needs public in-game context rather than a universal reroute.

## Important correction discovered by this diagnostic

KEXP-014's "8C/6S" group classified the **physical farm composition observed at step 672**. It was not a direct read of COK V8's internal route label.

The first version of KEXP-016 incorrectly treated every sampled row as the static no-Yarn/no-milk default branch. The fail-closed diagnostic caught a counterexample containing `SMOOTHIE_SHOP`. The tool was corrected before using its output for policy design.

The final report now records both:

- the public physical state;
- the static first-three-shop COK route signal.

No validation or held-out seed was touched by the correction.

## Corpus and result

Four already-open development seeds × both seats × three exact modern opponents = **24 complete baseline episodes**, zero runtime failures.

Static `8c6s_3q` default rows among the eight sampled rows per opponent:

- Kaito V27: **8/8**;
- Rayk V11: **6/8**;
- Andrew V12: **5/8**.

This confirms that the late observed 8C/6S production shape can arise even when the earlier shop-prefix selector did not choose the static default route. Future selector work must distinguish route intent from late physical state.

## Most informative conflict: seed 163219477

For both seats on `163219477`, all three opponent families expose the same first-three shops:

`BRUNCH_SPOT, BAKERY, FARMERS_MARKET`

and the same static COK route signal `8c6s_3q`.

At the first three-shop boundary, the public **our-money minus opponent-money** gap is:

- Rayk V11: **+1047**;
- Kaito V27: **+831**;
- Andrew V12: **+670**.

COK-style public layout L1 distance is much less discriminative there:

- Rayk: 35;
- Kaito: 35;
- Andrew: 36.

KEXP-015 outcome response on this seed:

- Rayk baseline: two losses at -1188; default→10C/4S: two wins at +1833;
- Andrew baseline: two narrow wins (+392, +204); default→10C/4S: two losses (-2449, -4077);
- Kaito baseline: two losses at -3516; default→10C/4S improves both to -829 but does not flip the outcome.

So **public economic divergence is a plausible selector feature**, while raw layout distance alone cannot explain the conflict. This is still discovery evidence, not permission to hard-code a threshold: opponent family and money gap are highly correlated in this tiny 24-row sample.

## Artifacts

Run `32968422225`:

- Kaito artifact `9606674181`, ZIP SHA-256 `928e1377e4b219e89ba498c22da46ad1cff75bd7a1d57017d6c2e2a86ea7f5f5`;
- Rayk artifact `9606672044`, ZIP SHA-256 `436c092faeaab12d36391bed39e61f02e35f892b0a52bf541c3b8b17b07a277c`;
- Andrew artifact `9606666107`, ZIP SHA-256 `d455a05223fc9c2a2adf50eb8086634f02da0deb15a14ea1e4ae5a1698b9f587`.

## Next step

KEXP-017 replaces threshold guessing with a solver-inspired **macro-policy oracle** over all 16 development seeds, both seats and all three modern opponent families. For every context it evaluates frozen R4B, default→10C/4S and default→6C/8S with the exact engine, labels the ex-post best macro branch, and then asks whether that expensive oracle can be distilled into a compact policy using only legal public features.

Seed ID, opponent identity, future outcome/actions and opponent private inventory are forbidden deployment features.

## Leakage policy

- development: open;
- validation: closed for changed R4D code;
- held-out: sealed 32/32.
