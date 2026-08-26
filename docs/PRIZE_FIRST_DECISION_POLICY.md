# Prize-first technical decision policy — Kculture

## Mission

The only project-level objective is to maximize the probability of a **top-10 Kaggriculture finish**. Methods are interchangeable means to that end.

## Core rule

**Every idea is a hypothesis, not a directive.**

This applies equally to:

- ideas suggested by the user;
- ideas suggested by the assistant;
- popular Kaggle techniques;
- public high-scoring agents;
- solver / planner / ML / evolutionary-search proposals;
- elegant engineering ideas.

Do not change the roadmap merely because a technique was mentioned in conversation.

## Decision test

Before committing substantial engineering time, answer:

1. **Failure target:** which observed competition weakness could this idea fix?
2. **Evidence:** what facts support the mechanism?
3. **Ceiling:** how many W/L outcomes could plausibly improve if it worked perfectly?
4. **Cheap falsification:** what is the smallest experiment that can kill the idea quickly?
5. **Generalization:** does the gain survive different seeds, seats and opponent families?
6. **Hosted relevance:** is the mechanism plausible for the live field, especially when hosted and local evidence disagree?
7. **Opportunity cost:** is this more valuable than the best competing experiment we could run with the same time/compute?

## Metric hierarchy

1. competition-aligned W/L/T and expected final-rank effect;
2. robustness across distributions/opponent families;
3. hosted calibration evidence;
4. execution legality/reliability;
5. terminal money margin as diagnostic/tiebreak evidence;
6. elegance, simplicity and novelty only after performance.

## Experiment policy

- Prefer cheap, bounded experiments before full architecture builds.
- Predeclare the comparison and promotion criterion when practical.
- Preserve exact hashes/versions/seeds and both-seat tests.
- Use development freely; changed code gets fresh validation after freeze.
- Keep held-out sealed until later promotion/final selection.
- A negative result is useful if it closes a branch and saves future effort.
- Never reinterpret a failed W/L experiment as success merely because money margin improved.

## Hosted/local conflict policy

The hosted ladder is not perfect evidence early in a rating process, but it is **real competition evidence**. A large contradiction between hosted results and local public-agent tests must be treated as a calibration failure in the laboratory model.

When conflict exists:

- do not dismiss hosted results as noise without evidence;
- do not blindly optimize to a few hosted games either;
- seek episode-level hosted data;
- broaden opponent and seed distributions;
- verify environment/package parity;
- prioritize mechanisms that explain both local and hosted observations.

## Architecture policy

There is no preferred architecture.

A heuristic can beat a solver. A solver can beat a heuristic. A small hardcoded fix can be worth more than a sophisticated model. Evolutionary search, ML, model-predictive control, rule systems and public-agent derivatives all compete on the same criterion: **expected prize value per unit of risk/time/compute**.

Architectural pivots require evidence of meaningful headroom.

## KEXP-017 precedent

The solver question produced a bounded macro-oracle test over three existing policy branches. Perfect ex-post branch selection improved the controlled modern panel only from **81-15 to 83-13**, with zero W/L improvement against Kaito or Andrew. Therefore a solver/selector over those branches was deprioritized instead of becoming the project architecture.

This is the desired behavior: test an interesting idea cheaply, measure its ceiling, and keep or kill it based on evidence rather than enthusiasm.
