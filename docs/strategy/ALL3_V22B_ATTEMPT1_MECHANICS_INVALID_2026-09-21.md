# ALL3 V22B Fresh Frontier Domain Upper Bound — Attempt 1 Mechanical Failure — 2026-09-21

Workflow: **`35566168354`**  
Launch commit: `66ae1cec7bae766ab62915cac711a73cafdf1ee3`  
Aggregate artifact ID: `10624696070`  
Aggregate digest: `sha256:d8975ef8507d5a0bb0126d2e6da36dfc05d6330f31dcae3c43a735cd69034af2`

Decision: **`V22B_MECHANICS_INVALID`**.

## Mechanical diagnosis

The failure was not caused by BASE replay mismatch, source SHA drift, episode invalidity, or treatment logic.

Observed shard status:
- shard 1: PASS, 23 contexts / 92 rows / 0 failures;
- shard 0: FAIL, 36 rows / 14 failures;
- shard 2: FAIL, 24 rows / 17 failures;
- shard 3: FAIL, 36 rows / 14 failures.

All **45 recorded failures** were in phase `teacher_acquire` and were Kaggle HTTP **429 Too Many Requests** errors from:
- `GetKernel`, or
- `DownloadKernelOutput`.

The same exact refs/SHAs were successfully acquired and executed by shard 1, which rules out a source incompatibility diagnosis.

The invalid partial aggregate contained only 47/92 contexts and must not be used for strategic decision-making.

## Mechanical repair

The V22B hypothesis remains unchanged:
- same 92 hard contexts;
- same exact source refs/SHAs;
- same seeds;
- same seats;
- same modes BASE / MARKET_ONLY / PHYSICAL_ONLY / FULL_SHADOW;
- same decision thresholds.

Mechanical changes only:
1. acquisition retries increased from 5 to 8;
2. retry wait changed to bounded exponential backoff (5, 10, 20, 40, 60... seconds);
3. matrix execution serialized with `max-parallel: 1` to avoid concurrent Kaggle acquisition bursts.

Repair commits:
- `8b50329e74163e59bf734067c931bbdaa340e6ae`;
- `ade4a4180d7081e57f7cde7286c9de07abfe2e87`.

Corrected binding rerun:
**`35607214335`**.

No Kaggle submission is authorized.
