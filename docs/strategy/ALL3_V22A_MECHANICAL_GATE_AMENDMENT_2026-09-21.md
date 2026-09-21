# V22A Mechanical Gate Amendment — 2026-09-21

## Status

This is a **mechanical-only correction identified before any V22A strategic outcome was available**.

Original run:
- workflow: `35560761804`;
- launch commit: `b57a5aa37249e9629233b7f11fe300ffc267cb94`;
- status at discovery of the defect: still `in_progress`;
- no artifact/result/log outcome had been read.

## Defect

The pre-registered V22A branch requires:

- zero source acquisition failures after bounded retry;
- zero source smoke/runtime failures;
- exact mechanically valid census before the READY gate is evaluated.

The initial V22A script incorrectly allowed `mechanical_pass=true` when:
- some Top-30 acquisitions failed, or
- some unique sources failed both-seat smoke,

provided at least eight selected sources and all selected episodes completed.

That was weaker than the frozen protocol and could have produced a false READY.

## Correction

Commit:
`addc89c11b6cd1f73f5cf764f7226db1c17caaca`.

The mechanical gate now additionally requires:

- `not acquisition_failures`;
- `not smoke_failures`.

Nothing strategic changed:
- same current Top-30 query;
- same SHA deduplication;
- same V47/self exclusion;
- same up-to-12 representative selection by current rank only;
- same seeds `79101..79106`;
- same seats `0,1`;
- same >=96-context requirement;
- same READY requirement of >=12 nonwins across >=4 source SHAs and >=3 seeds;
- same ALL3 candidate;
- same no-submission rule.

## Binding consequence

Workflow `35560761804` is NON-BINDING regardless of its eventual conclusion.

A corrected V22A run must be launched from the amended script and becomes the sole binding V22A execution.

No strategic information from the non-binding run may be used.
