# Decision — Public development during active competition

Date: 2026-08-25

## Decision

Kculture will remain a **public GitHub repository** during the active Kaggriculture competition.

The owner explicitly accepts the practical risk that competitors could discover and inspect the repository. The benefit is unrestricted use of public GitHub Actions for repeated deterministic simulation and regression testing.

## Consequences

- Competitive candidate code, builders, evaluation configs, and results may be committed publicly.
- Public third-party competition code may be used only when its source/license/provenance are preserved and its use is compatible with Kaggle's public-code-sharing rules.
- No private/unpublished competitor code, credentials, browser state, or redistribution-restricted replay payloads may be committed.
- Every imported public agent must be pinned by repository, commit, path, SHA-256, and license.
- Public discovery risk is accepted and is not a blocker for R4-R9.

## Strategic rationale

The immediate performance gap is too large for starter-level incremental work: the frozen starter earned roughly 3.7k-4.4k coins in calibration while strong public agents produced roughly 150k on the same engine. Public licensed policies therefore serve as legitimate engineering baselines. Kculture's competitive work will focus on independent screening, robustness, engine-1.32.7 adaptation, failure analysis, and measured improvements rather than rebuilding already-public route infrastructure from scratch.
