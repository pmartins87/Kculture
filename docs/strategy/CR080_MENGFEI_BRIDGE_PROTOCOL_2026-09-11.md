# CR080 Mengfei route bridge — protocol

Frozen 2026-09-11 before holdout scoring or any new H2H.
CR079 has FAIL result in run 34562284953; do not rerun/tune it.

## Sources and separation

Mengfei recent corpus: run 34558022808, artifact 10183391523,
SHA256 c0d4891e2064dd1cebe6a3f0de27a2a67ee330fb1941163b19b3ea003283e2b7.
128 unique-target episodes; oldest 96 for development, latest 32 for offline
chronological diagnostics. Episode chronology comes from API createTime.
Development action inspection is allowed. Neither holdout rewards nor actions
may select routes, weights, candidate parameters or stopping rules.
Replay alignment: observation t -> action frame t+1. Do not use configuration
seed, names, episode identity, rewards, future or opponent private information.
Retain exact source IDs only in build provenance, never policy features.

## Hypothesis and implementation boundary

The Mengfei family has a strong repeatable route backbone and should be
reconstructed at route/block level, rather than mixing independent actions.
Build exactly one executable CR080 using the development corpus. Select coherent
24-turn daily routes at the day boundary with physical farm/worker compatibility
first, public shop context second, and economy/inventory compatibility third.
Keep the selected route for the entire day. No per-turn reselection or extra
market speculation. Runtime may add mechanical route-following safety (legal
clock, movement to route positions, DIG before planting on a weed, available
stock handling) only if documented before tests. Selection must never look at
future shop unlocks. Preserve current action and market order semantics.

Before scoring, append the exact selector and mechanical behavior specification,
source/model hashes and training manifest. Freeze candidate first.
Offline action fidelity is descriptive: it is not a W/L estimate, nor a hard
SpaTaro-style architecture gate. The material question is closed-loop performance.

## Bounded gates

1. Build and package smoke in official environment 1.32.7, both seats; validate
   pre-action alignment and legal field allowlist. Zero exceptions/non-DONE.
2. Fresh discovery: CR080 vs CR071M, 8 seeds x 2 seats, master 9112080.
   Require score_rate >= 0.625 and zero exceptions/non-DONE. A lower result closes
   this frozen bridge; do not tune it on these seeds. Smoke outcomes count as
   discovery and must not be used to adjust strategy.
3. If discovery passes: one independent confirmation, master 9112081, 32 seeds
   x 2 seats vs CR071M and CR053/CR061/CR065 guardrails; run CR071M against the same
   three guardrails. Require direct score >=0.5625, aggregate guardrail delta >=0,
   no individual delta below -0.0625, and zero errors/non-DONE.
4. Stop local expansion at that result. PASS makes one controlled hosted probe
   eligible after active-slot accounting; offline/old-agent results do not prove
   top-10 strength. FAIL closes CR080, retains corpus and records the causal
   failure before choosing a new architecture. Never recycle the failed holdout.

The 32 original final held-out seeds remain sealed. Generate and check these
new seed lists against previous recorded master seeds before running.
No automatic Kaggle submission is included in any workflow.

## Continuation contract

Update STATUS.md and ROADMAP.md for current state; this protocol supersedes old
immediate actions that requested a repeat CR071M submission. API-first policy
remains active. Kaggle snapshot must query 56124705/current submissions; the
legacy scheduled workflow still queries obsolete R4B/KEXP050 and is not a
current CR071M checkpoint.

## Exact selector and runtime — frozen before CR080 evaluation

Runtime: `candidates/cr080_mengfei_route_bridge.py`; builder:
`tools/cr080_build_mengfei_bridge.py`. One bank of the 96 full training trajectories.
Each day selects a full 24-action block from one trajectory, without within-day
reselection. Ordered lexicographic minimization:

1. `10 * farmer Manhattan distance + differing physical tile codes + 25 * quadrant symmetric difference`;
2. L1 distance between public shop multiplicity counts;
3. L1 distance of log1p own money, own shed/seeds quantities, shared market prices
   and inventory, using a fixed item vocabulary;
4. chronological training bank ordinal, solely a deterministic tie-break.

Physical tile codes retain kind, crop/animal and planted/placed age. Weeds count
as empty space for route selection; runtime substitutes DIG for PLANT/WATER/
HARVEST on weeds. Farmer/hand roles are ordinal slots from the official schema,
not opaque worker IDs. The initial claim that these replays require UUID remapping
was not supported by this corpus. At a position mismatch, move toward the route's
expected position (or expected next position for a movement action), x-axis first.
Missing hand actions become PASS; extra reference hands are omitted. All market
orders retain source order and quantity, capped at 10. No new sells, spending,
market front-runs, smoothing or fitted outcome weights are introduced.

The archive contains only runtime and training action/signature/position bank.
Names, episode IDs, metadata, rewards and source seeds remain outside the archive.
Exceptions are visible to the official harness, never silently converted to PASS.
Build gzip and tar timestamps are deterministic (zero). Fresh split/model/package
hashes are saved in build_receipt.json before evaluating.

Closed-loop drift (route position correction, unfilled orders, low farm output)
is a concrete risk. The short W/L screen is deliberately the stop gate for this
risk; an attractive offline reconstruction score cannot override a failed screen.
