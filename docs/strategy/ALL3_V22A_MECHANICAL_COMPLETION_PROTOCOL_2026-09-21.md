# ALL3 V22A Mechanical Completion Protocol — 2026-09-21

## Status

DORMANT / PRE-REGISTERED BEFORE ANY BINDING V22A OUTCOME.

Binding V22A workflow:
`35562142399`.

This protocol activates only if that corrected binding run returns
`V22A_MECHANICS_INVALID`.

## Purpose

Repair acquisition/replay mechanics without changing the V22A strategic population or gate.

The corrected V22A gate is strict:
- current Top-30 must be captured;
- all attempted source acquisitions must resolve after bounded retry;
- all acquired unique sources must pass the frozen both-seat smoke;
- the selected executable pool must contain >=8 unique non-V47 source SHAs;
- all selected ALL3 episodes must complete;
- only then may residual difficulty be interpreted.

## Population freeze on mechanical failure

If binding V22A is mechanically invalid, freeze from its artifact/logs:

- the exact ordered `current_top30_refs` returned by the binding run;
- every successfully acquired `main_sha256`;
- every acquisition receipt;
- all selected representative rules;
- seeds `79101..79106`;
- seats `0,1`;
- ALL3 candidate identity.

A completion run must **not query the current frontier again**.

Therefore a later leaderboard/frontier drift cannot silently replace the failed population.

## Acquisition completion

For a failed ref:

1. retry the exact frozen ref with the same bounded retry policy;
2. if the unversioned ref now resolves to bytes different from an already observed/frozen SHA identity, search public historical versions for the exact intended bytes when such an intended SHA is available;
3. if no exact version can be resolved, mechanics remain invalid.

HTTP 429/temporary transport failure is mechanical, never strategic.

## Smoke completion

For an acquired SHA that failed smoke:

- reacquire the exact SHA/version;
- run the same exact engine `kaggle-environments==1.32.7`;
- same smoke seed `79100`;
- both seats;
- credentials removed before third-party execution.

No alternate smoke seed, timeout relaxation, source patching or code editing is allowed.

If exact source repeatedly fails the frozen smoke, V22A remains mechanically invalid.

## Episode completion

If selected ALL3 episodes alone are missing/fail:

- run only the missing exact keys
  `(source SHA, seed, seat)`;
- same exact source version;
- same exact ALL3;
- same seeds/seats;
- merge with already mechanically valid rows;
- verify the full expected key set before applying READY/TOO_EASY.

No context may be dropped because it is slow, difficult or unfavorable.

## Strategic gate after completion

The original V22A decision rule remains unchanged:

READY requires:
- >=8 unique executable frontier source SHAs;
- >=96 valid ALL3 contexts;
- zero source/replay failures;
- >=12 ALL3 non-wins;
- non-wins across >=4 source SHAs;
- non-wins across >=3 seeds.

No Kaggle submission.
