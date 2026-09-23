# V28G — ALL3 Residual Hard-Core Census Result — 2026-09-22

## Binding workflow

- workflow: `35812527508`
- job: `107027015333`
- decision: **`V28G_SOURCE_CLUSTERED_HARD_CORE`**

## Binding input

Frozen V28F aggregate from workflow `35807910104`.

No episode was rerun in V28G.

## Residual hard core

ALL3 residual losses:
**66 / 144**.

Universal-hard losses:
**66 / 66**.

Thus every context lost by ALL3 was also lost by V47, O-RW1, CR053 and CR029.

## Source concentration

Exactly six frontier sources generated every ALL3 loss; the other six generated zero losses.

Concentration:
- top-1 source share: 18.18%;
- top-2: 36.36%;
- top-4: **69.70%**;
- systematic sources with >=9 losses out of 12: **6**;
- moderate sources with 6–8 losses: 0;
- low sources with 1–5 losses: 0;
- zero-loss sources: **6**.

The frozen >=60% top-4 rule therefore classifies the residual hard core as source-clustered.

### Six hard sources

1. rank 4 — `dmitriigluzdov/kaggriculture-more-wheat-smarter-sales`
   - 12/12 losses;
   - median loss margin -3498;
   - 2 severe losses <= -10000.

2. rank 6 — `ahmedberatozer/kaggriculture-v53-opening-signature`
   - 12/12 losses;
   - median loss margin -3471.5;
   - 2 severe.

3. rank 15 — `dmitriigluzdov/kaggriculture-herd-safe-sale-window-lb-2700`
   - 12/12 losses;
   - median loss margin -3546.5;
   - 2 severe.

4. rank 7 — `ahmedberatozer/kaggriculture-v55-one-turn-market-race-edge`
   - 10/12 losses;
   - median loss margin -3952;
   - 2 severe.

5. rank 14 — `nihilisticneuralnet/kaggriculture-clone-race-horizon`
   - 10/12 losses;
   - median loss margin -4112;
   - 2 severe.

6. rank 16 — `nathanjacob/kaggriculture-pipe18-six-layers`
   - 10/12 losses;
   - median loss margin -4112;
   - 2 severe.

## Seat and seed

Seat is perfectly balanced:
- seat 0: 33/72 losses;
- seat 1: 33/72 losses.

Seeds:
- 80401: 6/24 losses;
- 80402: 12/24;
- 80403: 12/24;
- 80404: 12/24;
- 80405: 12/24;
- 80406: 12/24.

Thus the hard-source split is much stronger than seat effects. Seed 80401 is unusually favorable but does not eliminate the hard-source pattern.

## Loss severity

- close (margin >= -2000): **4**
- medium (-10000 < margin < -2000): **50**
- severe (margin <= -10000): **12**

Two extremely close examples are:
- rank 4, seed 80401, seat 0: ALL3 margin **-7**;
- rank 15, seed 80401, seat 0: ALL3 margin **-12**.

## Existing option effect inside losses

Against V47 on the exact same 66 losing contexts:
- ALL3 margin better: **62**
- worse: 4
- equal: 0
- mean ALL3-minus-V47 margin delta: **+89.91**
- median delta: **+61**

Against O-RW1:
- ALL3 better: **62**
- worse: 4
- mean delta: **+90.39**
- median delta: **+54**

Interpretation: the current option stack usually improves economic outcome inside the hard core, but the gains are far too small to change W/L.

## Binding interpretation

The residual weakness is not broad stochastic failure. It is a sharply source-clustered structural regime spanning six current frontier policies.

The next gate should compare deterministic hard contexts against matched zero-loss-source controls using the same seeds/seats and inspect:
- phase-level money gap;
- public farm composition;
- own legal private inventory;
- market and physical action allocation;
- ALL3 option-trigger timing.

Opponent identity remains offline forensic metadata only and cannot become a runtime policy feature.

No Kaggle mutation is authorized.
