# STATUS — Kculture live source of truth

Updated: 2026-09-11 local / 2026-09-12 UTC boundary

Authoritative working branch: `fix/kaggle-parity-v1`. Historical detail remains available in Git history; this file intentionally contains only the current operational state.

## Mission

Maximize the probability of a prize-winning / top-10 Kaggriculture result. Final deadline remains 2026-09-30 23:59 UTC. Do not spend a hosted submission on a candidate that has not passed its frozen gate.

## Incumbents / hosted reality

- CR071M — submission `56124705`; authenticated checkpoint: rating **1731.8**, 297 listed episodes. Newest 32 replays: 8W / 22L / 2T, score rate 0.28125. It remains the incumbent reference, not an architecture worth microtuning.
- CR070A — submission `56091951`; authenticated rating **1724.0**. Newest 32: 8W / 19L / 5T, score rate 0.328125.
- Do not submit CR080 or any invalid CR081-v1 package.

## Closed candidates

- CR078 mirror breaker: closed / FAIL.
- CR079 SpaTaro simple 1-NN behavioral clone: closed / FAIL. Run `34562284953`; composite 0.28566 vs clock 0.37223, worse in 51/51 holdout episodes. No threshold retuning.
- CR080 Mengfei route bridge: closed / FAIL. Independent confirmation run `34655496708`: direct vs CR071M 33–31 = 0.515625 and large guardrail regression vs CR061/CR065. No CR080A/B/C rescue.
- CR080 failure diagnostic run `34668446703` completed: no hand shortfall, omitted hand actions, position mismatch or market mismatch. Losses show materially larger economic-state drift. Conclusion: nearest-route/day replay stitching fails through economic state aliasing; that architecture class is closed.

## Current frontier — authenticated API snapshot

Run `34668645531`:

1. Majkel1337 — **3181.9** — `56156662`;
2. ymg_aq — **3075.1** — `56161578`;
3. Unknown Mother-Goose — **3056.5** — `56169353`;
4. Artem The Farmer — **3029.3**;
5. SpaTaro — **3029.0**.

The preferred bridge target is current #3 Unknown Mother-Goose (UMG), because recent CR071M hosted losses against a related family preserve much of the physical lineage while materially changing market/economy behavior.

## CR081 Gate A — PASS

Deep corpus run `34669006417` completed. UMG exposed 111 episodes; one UMG-vs-UMG episode was seat-ambiguous and excluded, leaving **110 usable = 82 development + 28 newest holdout**. Majkel newest64 and ymg_aq newest64 were also collected for context.

Runtime-aligned Gate A on the 28 newest UMG holdout episodes:

- farmer similarity to frozen bridge family: median **0.90104**, required >=0.80;
- hands similarity: median **0.73958**, required >=0.60;
- development-only step-modal market policy -> holdout market fidelity **0.94959**, required >=0.65.

Gate A therefore passes without threshold adjustment.

## Critical replay-index correction

Kaggle stores `steps[s].action` as the action that produced replay state `s`; runtime `observation.step=t` maps to replay action index **t+1**. This was verified against hosted CR071M, where replay farmer/hands at index `s` match the known CR071M route at `s-1` exactly over the checked prefix.

Consequences:

- the earlier apparent one-turn-delayed UMG physical backbone was a replay-storage artifact;
- **CR071M physical/runtime backbone must remain same-step and unchanged**;
- UMG replay market actions 1..288 map to runtime steps 0..287;
- runtime-aligned stable-prefix support remains strong: market ~0.970 / 0.942 / 0.914 over the first three 96-step blocks, dropping to ~0.683 in the next block;
- the 288-step boundary remains valid;
- UMG's `BUY_PRODUCT WHEAT 13`, `BUY_PRODUCT WHEAT 36`, `SELL WHEAT 36` mechanism occurs at **runtime step 0**.

Workflow run `34671122716` was launched before this indexing bug was caught and contains a delayed physical backbone. It is **INVALID / SUPERSEDED**. Ignore any strategic result it produces. The connector available in-chat does not expose workflow cancellation, so quarantine is enforced by documentation and by using a different seed master.

## Active corrected confirmation

Corrected workflow: **run `34671446692`**, `CR081 current-3056 bridge confirmation v2`.

Candidate:

- unchanged same-step CR071M physical/runtime backbone;
- runtime steps 0..287 receive UMG development-only modal market queue from replay indices 1..288;
- original CR071M safety/repair logic retained;
- sequential same-turn BUY_PRODUCT is credited before later SELL during prefix clamping;
- no replay stitching, target identity feature, seed, future state or opponent-private state.

Fresh master seed: **9120812**, explicitly firewalled against CR080 masters and invalid CR081-v1 seed master 9120811.

Frozen promotion gate remains:

- 32 seeds x two seats = 64 games/H2H;
- CR081 vs CR071M direct score >=0.5625;
- guardrail aggregate delta vs CR053/CR061/CR065 >=0;
- each guardrail delta >= -0.0625;
- zero errors/non-DONE.

PASS -> exact tested hash becomes eligible for one hosted probe after slot accounting. FAIL -> close CR081 bridge and move directly to current-frontier state-adaptive macro-economic policy; no CR081A/B/C threshold rescue.

## Operational policies that remain binding

- Authenticated Kaggle API first; screenshots/UI only as fallback.
- Exact local H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- No team name, episode ID, seed, future information or opponent private state as an agent feature.
- Original final holdout remains sealed.
- No automatic hosted submission without a passed frozen promotion gate.
- Closed hypotheses stay closed unless genuinely new evidence invalidates the reason for closure.
