# O-LQ2 + O-RW1 + O-TW1 Triple Composition — Result — 2026-09-19

## Binding run

Workflow: **`35456535323`**  
Head: `c3e5dba49185f38693593ace0a3cd2a3a47a89d7`  
Aggregate artifact: `10588433539`  
Aggregate digest: `sha256:d9b9f7939a72dd79df340c313eac73a9a1b89e953138db451a7f643b758dc9ad`.

Mechanical PASS:
- 7/7 opponent blocks;
- 56/56 fresh contexts;
- zero failures;
- exact pre-trigger V47 parity;
- no physical-action mutation.

## Binding decision

**`TRIPLE_COMBO_SAFE_ADVANCE`**

Variants:
- BASE = exact V47;
- OLD = O-RW1 + O-TW1;
- LQ2 = O-LQ2 only;
- ALL3 = O-RW1 + O-TW1 + O-LQ2.

Overall score rates:
- BASE: **0.7857143**;
- OLD: **0.8392857**;
- LQ2: **0.9464286**;
- ALL3: **0.9464286**.

Deltas:
- ALL3 vs BASE: **+0.1607143**;
- ALL3 vs OLD: **+0.1071429**;
- ALL3 vs LQ2: **0.0**;
- ALL3 negative-score contexts vs BASE: **0**;
- ALL3 positive-score contexts vs BASE: **12**.

Mean terminal margin:
- BASE: 21,274.04;
- OLD: 21,374.23;
- LQ2: 21,571.48;
- ALL3: **21,671.68**.

## By opponent

### V48
- BASE: 0.125;
- OLD: 0.125;
- LQ2: 0.875;
- ALL3: **0.875**.

Mean margin:
- LQ2: +99.75;
- ALL3: **+140.0**.

So RW1/TW1 add margin without reducing LQ2 W/L headroom.

### V47 mirror
- BASE: 0.500;
- OLD: 0.875;
- LQ2: 0.875;
- ALL3: **0.875**.

Mean margin:
- OLD: +40.25;
- LQ2: +977.25;
- ALL3: **+1,017.5**.

### Other five families
Ready Stock, router_2715, conditional_memory, tactical_memory and best_market all remain W/L-neutral under ALL3.

## Integrated host decision

The current best deterministic offline host is now:

**exact hosted-faithful V47 + O-RW1 + O-TW1 + O-LQ2**.

Frozen operator order:
1. compute exact V47 current action;
2. if eligible and unused, O-TW1 has priority;
3. else if eligible and unused, O-RW1;
4. from step 336 onward, apply O-LQ2 canonical SELL queue to the resulting market action;
5. farmer/hands always remain exact V47.

This behavior is implemented in:
`tools/first_party_option_host_v1.py`.

## Next mandatory gate

Build a hosted-faithful single-file package from the exact pinned public V47 output package and append
only a standalone ALL3 wrapper.

Then prove:
- official-loader entrypoint parity;
- exact action-for-action parity against the in-process integrated host;
- exact reward parity;
- fresh seeds;
- multiple opponent blocks;
- both seats.

No Kaggle submission is authorized by this result alone.
