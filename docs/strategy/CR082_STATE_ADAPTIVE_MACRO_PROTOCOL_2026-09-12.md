# CR082 — state-adaptive macro-economic policy protocol

Status: **pre-registered fallback / parallel research**, not yet an executable candidate. It activates if CR081 v3 fails its frozen gate, or later as a successor architecture after a hosted CR081 probe.

## Why this architecture exists

CR080 closed nearest-route/day stitching because economic-state aliasing compounded across days. CR081 tests a stable UMG time-indexed market bridge. The next representation must not follow multi-step replay trajectories.

Exploratory analysis on the already-collected frontier corpora shows that **one-step legal economic state contains predictive signal beyond runtime step alone**, especially for current #1 Majkel1337. Using chronological 75/25 splits over runtime steps 0–287 and a same-step 1-NN on legal current economic state:

- Majkel exact market fidelity: step-modal **0.7949** -> state 1-NN **0.8498** (+0.0549); semantic fidelity 0.8162 -> 0.8707 (+0.0545).
- UMG exact: 0.9335 -> 0.9689 (+0.0353); semantic 0.9422 -> 0.9714 (+0.0291).
- ymg_aq exact: 0.7661 -> 0.7591; semantic 0.7873 -> 0.7910 (approximately neutral).

These existing holdouts are now **hypothesis-forming only** and may not serve as CR082's promotion evidence.

## Frozen representation

Primary teacher: **Majkel1337**, current frontier #1 in authenticated snapshot `34668645531` (submission `56156662`). UMG and ymg_aq are contextual diagnostics, not teacher-identity inputs at runtime.

CR082 is a **single-step state-conditioned market policy**, never a replay-route follower:

1. At runtime step `t`, compare only against teacher development examples from the **same runtime step `t`**.
2. Feature vector uses only legal current observation:
   - day, hour;
   - own money, number of hands, hires_today, number of unlocked quadrants;
   - own private shed quantities for products and animals;
   - own seed inventory;
   - public market prices;
   - public market inventory.
3. Standardize each feature using teacher-development statistics only.
4. Retrieve exactly one nearest teacher state from the same runtime step and copy **only that step's market queue**.
5. Never copy farmer/hands or continue a replay trajectory to the next step.
6. No team name, episode ID, seed, future state or opponent-private information.
7. OOD fallback is the teacher development-only per-step modal market queue. The accept/reject distance threshold must be frozen from teacher development data only using leave-one-out same-step nearest-neighbor distances; use the development **95th percentile** as the threshold.
8. Legal/capacity repairs are restricted to the same class allowed in CR081 v3: capacity `room_guard`, impossible-SELL clamping and same-turn BUY_PRODUCT->later-SELL accounting. No inherited opponent-specific market counter or `dead_stock` may alter the state-conditioned teacher queue inside the active prefix.

Initial active prefix is runtime steps **0–287**, matching the already-established current-frontier economic window. This may not be retuned on CR082 validation results.

## Fresh evidence requirement

Because the existing Majkel 64-episode corpus has already been inspected, CR082 Gate A requires a **new authenticated Majkel corpus collected after this protocol commit**. Replays whose EpisodeId already exists in the old 64-episode corpus are excluded.

Gate A uses newest fresh episodes chronologically and compares the frozen state-conditioned 1-NN against the frozen same-step modal baseline. It passes only if all hold:

- at least **24 genuinely new usable Majkel episodes**;
- exact market fidelity improvement >= **+0.03 absolute** over step-modal;
- semantic market fidelity improvement >= **+0.03 absolute** over step-modal;
- no identity/private-opponent features;
- no replay continuation across steps.

If fewer than 24 genuinely new episodes exist, Gate A is **not failed**; it remains pending until sufficient fresh evidence exists.

## Candidate construction if Gate A passes

Build exactly one CR082 candidate:

- CR071M physical/runtime backbone unchanged;
- runtime 0–287 market selected by frozen Majkel state-conditioned one-step policy;
- development-only OOD p95 fallback to Majkel per-step modal;
- only permitted legality/capacity repairs;
- normal CR071M behavior resumes after step 287.

Before any CR082 H2H result is viewed, freeze a fresh exact panel against the then-current incumbent plus CR053/CR061/CR065 and at least one current-frontier structural anchor if an exact package is available. Use new non-overlapping seeds.

## Closure rule

If fresh Gate A fails, do not tune k, features, p95 or the 288 boundary on that evidence. Move from imitation to explicit economic-value modeling / macro selection using game mechanics and current public state.
