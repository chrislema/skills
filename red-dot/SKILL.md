---
name: red-dot
description: "Build a complete custom diagnostic assessment (a 'where am I' quiz, scorecard, or self-assessment) for a domain expert's coaching or consulting offer, end to end. This is the entry point to the Red Dot pipeline: positioning, case intake, lifecycle mapping, outcome-space and gap design, question writing, deterministic scoring, report content, and gated assembly into a working artifact. Use whenever someone wants to turn expertise into an assessment, build a lead-gen quiz, design a scorecard, map where their clients get stuck, write or score quiz questions, draft result copy, or compile and ship a diagnostic. Start here even when the request names only one part; the router sends you to the right stage and names its upstream dependencies, so you can enter the pipeline anywhere."
---

# Red Dot — custom assessment builder

Red Dot manufactures, for a domain expert, the diagnostic their non-expert
customers need before they can hear advice. The thesis (see
[references/red-dot-system.md](references/red-dot-system.md)): place an honest
**dot** before any map or directions; the **gap** between the respondent's answer
and a benchmark they don't control is the product; **behavior, not self-report**,
is what makes that gap measurable and honest.

This skill is a **graph**, not a single procedure. This file is the router. The
work happens in eight stage nodes under `stages/`, which link forward to the next
stage and sideways to the shared concept nodes under `concepts/`. Read this file
to find the right entry point, then follow the links.

## The pipeline

The stages accumulate one `spec.json` (the single source of truth the engine
compiles). Each stage reads the spec the prior one left and adds its own keys.

0. [Positioning](stages/0-positioning.md) — the offer-first cut; what the assessment is *for*.
1. [Case intake](stages/1-case-intake.md) — concrete past-tense client cases, fenced from abstraction.
2. [Model induction](stages/2-model-induction.md) — the lifecycle map + stuck_map, by correcting a wrong draft.
3. [Outcome-space](stages/3-outcome-space.md) — **choose the gap**, design the address schema (most consequential).
4. [Instrument](stages/4-instrument.md) — the 10–15 questions.
5. [Scoring](stages/5-scoring.md) — a total, deterministic map from answers to an address.
6. [Content](stages/6-content.md) — every word of the report, gated.
7. [Assembly](stages/7-assembly.md) — compile, gate, emit. A broken assessment cannot ship.

## Router — enter anywhere

Match the request to a node. Each node names the upstream it relies on; if that
upstream output is missing from `spec.json`, go produce it first.

| If the request is… | Go to | First needs |
|---|---|---|
| "build / turn my expertise into an assessment", "where do I start" | [0 Positioning](stages/0-positioning.md) | — (start of pipeline) |
| "interview me about my clients", "capture how I diagnose" | [1 Case intake](stages/1-case-intake.md) | the positioning brief |
| "what are the stages", "map my domain", "where do clients get stuck" | [2 Model induction](stages/2-model-induction.md) | a case bank |
| "what should this measure", "what makes the result land", "how many result types" | [3 Outcome-space](stages/3-outcome-space.md) | the lifecycle map |
| "write the questions", "design the quiz items", "what should I ask" | [4 Instrument](stages/4-instrument.md) | the address schema |
| "how do I score this", "turn answers into a result", "validate the scoring" | [5 Scoring](stages/5-scoring.md) | the questions |
| "write the results", "draft the report copy", "what does each result say" | [6 Content](stages/6-content.md) | the scoring spec |
| "build it", "compile", "generate", "ship it", "put it together" | [7 Assembly](stages/7-assembly.md) | the content library |

You do not have to start at 0. If someone arrives mid-pipeline with the upstream
already in hand (or in an existing `spec.json`), jump straight to their node. If
the upstream is missing, the node says so — produce it, then return.

## Operating mode: interview vs. brief-only

The upstream knowledge arrives one of two ways, and the difference changes how
Stages 1–2 behave. Decide which mode you are in before you start, and carry it
through.

- **Interview mode (the default the prose assumes).** A live expert is in the
  loop. Stage 1 elicits cases by interview; Stage 2 shows a *deliberately-wrong*
  draft and harvests the correction. The wrongness is a tool to provoke the
  expert's correction reflex — it is scaffolding shown to a human and never
  reaches `spec.json`.
- **Brief-only mode (no interview).** The expert has written their perspective
  up front and the skill builds from it unattended. There is no correction loop,
  so the deliberate-wrongness step is **inert and must be skipped** — there is no
  one to correct a wrong draft, and producing one would only degrade the model.
  In this mode Stage 2 builds the *most accurate* model it can from the brief and
  routes every low-confidence inference to the design doc's §7 ("What's yours to
  correct") rather than planting it in the model. §7 is the surrogate for the
  missing live correction; the honesty gate forbids deliberate error in the
  shipped artifact regardless.

If you are running unattended from a written brief, you are in brief-only mode.

## Shared concept nodes

- [The kit](concepts/the-kit.md) — the recurring techniques and the gap-pattern vocabulary that ties stages together.
- [The gates](concepts/the-gates.md) — the §11 invariants, their severities, and how assembly enforces them.
- [The spec schema](concepts/spec-schema.md) — the canonical shape of `spec.json` every stage contributes to.

## Tooling (one home, run from the skill root)

- `scripts/validate_scoring.py spec.json` — reachability enumeration + the exemplar test (Stage 5).
- `scripts/engine.py spec.json out.html` — compile, gate, emit the runnable assessment (Stage 7). Add `--check` to gate without emitting.
- `scripts/design_doc.py spec.json out.md` — compile the human-readable **design document** from the same spec (Stage 7's second emit): the 2×2, names, lifecycle, every question + what it reads, the scoring variables, the gaps, and how content is assembled. This is the artifact the expert reads and corrects.
- `scripts/gate_check.py` — the importable standing checker the engine uses.
- `assets/example-spec.json` — a complete working spec (the two-strand-quadrant reference) to copy from.

## Scope of the bundled tooling

The engine and checker implement the **two-strand-quadrant reference pattern** —
the shape built and validated so far. The judgment in every stage is
domain-general; the reference scripts are quadrant-shaped until a richer address
schema (e.g. stage × locus × theme) stretches them. To generalize, extend the
resolver in `scripts/engine.py` (`reachable`, `compile_landings`) and
`scripts/gate_check.py` (`reachable_addresses`); the gate logic is unchanged.
`scripts/design_doc.py` shares the same resolver and the same scope; generalize
its `reachable` alongside the others.
