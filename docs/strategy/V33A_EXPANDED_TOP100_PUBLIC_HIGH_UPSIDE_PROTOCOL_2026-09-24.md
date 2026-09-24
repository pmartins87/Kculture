# V33A — Expanded Top-100 Public Policy High-Upside Sweep — 2026-09-24

## Status
PRE-REGISTERED after hosted V30B stabilized near 2391 and current Top-10 gap remained >500 rating points.

No V33A result authorizes Kaggle mutation.

## Purpose
Search a substantially broader public Competition Code population than V30A/V32A. V30A only acquired the first Top-30 public kernels and froze at most 12 executable SHA-unique representatives. V33A expands discovery to the first 100 current public competition kernels, so ranks beyond the prior frozen representative set can enter.

## Discovery
Use:
`kaggle kernels list --competition kaggriculture --sort-by scoreDescending --page-size 100 -v`

Acquire every returned ref with the existing audited public-source loader.
Deduplicate by exact `main.py` SHA.
Smoke every SHA-unique policy against starter in both seats.
Exclude exact SHAs already present in immutable V30A and V32A selected snapshots.
Freeze the first **40** remaining executable SHA-unique representatives by current kernel rank, or all if fewer.

If zero new executable unique policies:
`V33A_NO_NEW_EXPANDED_PUBLIC_POLICY`.

## Baseline
Exact hosted V30B:
- ref `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`;
- SHA `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`.

## Opponent panel
Acquire a separate fresh standard V28B Top-30/12-representative immutable frontier after preregistration.

## Stage-A benchmark
Every new candidate and exact V30B baseline run on identical:
- all frozen opponent sources;
- seeds `80901,80902,80903`;
- both seats.

## High-upside gate
A new policy advances only if all:
1. mechanics PASS;
2. candidate score rate >= V30B + **0.10**;
3. mean paired score delta >= **+0.10**;
4. positive source breadth >=4;
5. positive seed breadth =3/3;
6. positive contexts > negative contexts;
7. positive support in both seats.

Selector among eligible:
score rate -> paired score delta -> paired margin delta -> source breadth -> lower current rank -> lexical SHA.

Decisions:
- `V33A_EXPANDED_PUBLIC_CHALLENGER_READY`
- `V33A_NO_NEW_EXPANDED_PUBLIC_POLICY`
- `V33A_EXPANDED_PUBLIC_NO_HIGH_UPSIDE`
- `V33A_MECHANICS_INVALID`.

Routing:
READY => freeze exact ref/SHA/package and launch one V33B fresh independent validation on new frontier and seeds.
NO_NEW/NO_HIGH_UPSIDE => close expanded-public sweep.
No hosted submission without explicit user authorization.
