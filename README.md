# RL Engineer Take-Home: Synthetic Pipeline for WebGL Landing Page Tasks

Synthetic pipeline that generates RL tasks for a coding agent writing visually stunning WebGL landing pages: the briefs, the graders, and the quality gates that decide which generated tasks are fit to train on. Tasks ship as Harbor bundles.

**Role:** RL Engineer (Environments & Rewards)  
**Time budget:** 2 days

## What this is

You are building a **task factory**, not the landing pages and not a trained model.

- An agent will later be asked to write a single-file WebGL / Three.js scene.
- This repo produces many different challenges (briefs + constraints) automatically.
- For each challenge it generates a grader and packages everything as a Harbor task bundle.
- Quality gates filter out bad tasks before they are accepted.

## High-level plan (step by step)

1. **Taxonomy & sampling**  
   Define axes (product category, mood, motion budget, palette, required copy, interaction, constraints).  
   Combinatorially sample them into structured **constraint specs** (the source of truth).

2. **Brief synthesis**  
   Use an LLM to expand each constraint spec into a readable natural-language brief.  
   Keep prompts versioned in `pipeline/prompts/`.

3. **Grader synthesis**  
   From the same constraint spec, automatically generate the gates and checks for that task (not one hand-written grader for everything).

4. **Instruction rendering**  
   Generate agent-facing `instruction.md` from the spec, stripping grader details.  
   Mechanically check for leaks.

5. **Quality gates**  
   Run automatically on every generated task:  
   - Oracle run (reference solution scores well)  
   - NOP run (empty submission scores 0)  
   - Leak check  
   - Difficulty probe  
   - Flake check  
   - Diversity check  
   Report yield: generated / rejected / accepted.

6. **Harbor packaging**  
   Emit valid Harbor bundles (`task.toml` schema 2.0, environment/, tests/, solution/, etc.).

7. **Reward / scorer**  
   Shared continuous scorer with at least three signal families (gates, render-based, code/parameter).  
   Callable as a pure function.

8. **Renderer harness**  
   Headless Chromium capture with determinism controls (pinned browser, stubbed clock, seeded RNG, virtual time).

9. **Report**  
   Write `report.md` covering what was built, signal quality, headroom, hackability, stability, cost, and a final verdict (train / evaluate / both / neither).

## Required commands (to implement)

- `make pipeline` — one command, takes count + seed, produces 50 Harbor bundles deterministically.
- `make quality` — runs the six gates and writes the yield report.
- `make score <bundle> <submission>` — returns scored breakdown.

The scorer must also be callable as a pure function from (brief spec, submission) → scored breakdown.

## Repository layout

```
pipeline/            brief synthesis, grader synthesis, instruction rendering
pipeline/prompts/    every generation prompt, versioned
quality/             the six gates, the reject log, the yield report
tasks/               50 generated Harbor bundles
reward/              the shared continuous scorer, weights, config
renderer/            headless capture harness, determinism controls
rollouts/            raw episode logs, scores, captured frames
report.md            Part E
README.md            this file
```

## Assumptions & notes

- No GPU required; software rasterizer is acceptable.
- LLM calls for brief expansion only; structured specs and gates are programmatic.
- Determinism: same seed → same tasks; same submission scored twice → same gates and code-derived terms.
- See the original assignment for full Harbor contract and grading criteria.

## Status

Scaffold only. Implementation of the pipeline, graders, quality gates, and renderer still required.
