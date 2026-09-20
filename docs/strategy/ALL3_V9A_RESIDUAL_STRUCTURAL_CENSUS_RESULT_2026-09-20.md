# ALL3 V9A Residual Structural Census — Result — 2026-09-20

Workflow: **`35517515758`**  
Launch commit: `a551a38023ee268b43f71ed442b998a99d547a40`

Decision: **`V9A_STRUCTURAL_RESIDUAL_READY`**

Mechanical:
- PASS;
- exact ALL3 replay matched all four frozen hard-context margins/scores;
- failures 0;
- physical divergences: **0**.

Residual market divergences:
- total: **233**;
- INSERT_DROP: **161**;
- QTY_UP: **63**;
- REORDER_ONLY: **9**.

All four hard contexts contain structural residuals.

Per context:
- context 0: 59 divergences = 37 INSERT_DROP + 21 QTY_UP + 1 REORDER_ONLY; first structural turn 80;
- context 1: 58 = 43 + 11 + 4; first structural turn 153;
- context 2: 57 = 44 + 10 + 3; first structural turn 80;
- context 3: 59 = 37 + 21 + 1; first structural turn 80.

Conclusion:
ALL3/LQ2 does not exhaust V48's market mechanism. The residual is not physical and is overwhelmingly structural insertion/drop plus quantity increase behavior. V9B is therefore authorized by the pre-registered gate.

No automatic Kaggle submission.
