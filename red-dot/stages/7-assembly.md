
# Red Dot - Assembly (Stage 7)

> **Stage 7 of 8 — Red Dot pipeline.**
> ← prev: [content](6-content.md)
> Shared nodes: [the gate machinery](../concepts/the-gates.md), [spec schema](../concepts/spec-schema.md)

Compile, gate, emit. The spec is the single source of truth; the engine generates the artifact from it; the checker validates the compiled surface and refuses to emit on any blocking failure. Because the checked surface and the rendered artifact are compiled from the same spec, they cannot drift.

## Contract

- **Consumes:** the full spec.json (every prior stage's keys).
- **Produces:** TWO artifacts from the one spec — (1) the runnable assessment (a self-contained HTML file at the reference tier), and (2) the human-readable **design document** (markdown): the framework laid out flat for the expert to read and correct. Both compile from the same spec, so they cannot drift from each other or from the gated surface.
- **Owes the rest of the system:** bijection verified at compile and a full invariant lint that must pass before the HTML is emitted.

## Method

Run the engine. It compiles the spec into per-address landings, runs the
gate-checker on that compiled surface, and writes the artifact ONLY if every
blocking gate passes:

```bash
cd scripts
python engine.py ../spec.json ../assessment.html
```

To gate-check without emitting (e.g. after editing the spec):

```bash
python scripts/engine.py --check spec.json
```

Emit the design document from the same spec (no gating — it's a read of the
spec, not a runtime surface). Produce it whenever the expert needs to *see and
correct* the framework rather than click through paths:

```bash
python scripts/design_doc.py spec.json design.md
```

It derives the 2×2, the quadrant names, the lifecycle, every question with what
it reads, the scoring variables, the gaps, and the assembly model straight from
the spec. A few OPTIONAL spec fields enrich it when present (and are ignored by
the engine): `question.reads` / `question.catches`, a `label` on any
non-self/team axis, and a `design_notes` block (`thesis`, `benchmark_note`,
`woven_not_scored`, `corrections`). Edit the spec, re-emit, and the document and
the assessment stay in lockstep.

The checker is tier-aware: gates that need advanced structure (detectability,
commercial closure, two-faced coverage, ranking-gap-derived, positional
rationale) read as N/A until the spec contains a stuck_map, an offer, maturity
stages, or a ranking, at which point they activate as blocking. The engine and
checker bundled here implement the two-strand-quadrant reference pattern; for a
richer address schema, generalize the resolver in both.

## Craft rules and failure modes

- **Drift is structurally prevented.** Never hand-edit the emitted artifact; edit
  the spec and recompile. A failing spec produces no artifact at all.
- The reference engine emits a single self-contained HTML file (Tier 0/1 core,
  no backend). Persisting sessions, an email gate, and an edge deployment
  (Workers + KV) are the Tier-1 plumbing AROUND this core, added separately.
- Re-run the gate-check after ANY spec change; a green check is the ship signal.

## Output — what you write into `spec.json`

The engine reads: `spec.meta`, `spec.questions`, `spec.scoring`, `spec.content`,
`spec.banned_phrases`, and (when present) `spec.stuck_points`, `spec.offer`,
`spec.maturity_stages`, `spec.ranking`. It writes no new spec keys — it consumes
the spec and emits the artifact. See `references/spec-schema.md` for the full
canonical shape every stage contributes to.

## Gates this stage must satisfy

Enforces all blocking gates before emit: **Coverage, Bijection, Gap present,
Evidence, Voice gate, No orphan questions, Honesty gate** — plus the tier-aware
gates once their structures exist. Reports advisories (introspective items,
content cue) every run. If any blocking gate fails, the engine aborts and writes
nothing.

## Bundled scripts

- `scripts/engine.py` — compiles spec to a self-contained HTML artifact; gates before emit.
- `scripts/design_doc.py` — compiles the same spec to the human-readable design-document markdown (the expert's correction surface).
- `scripts/gate_check.py` — the standing invariant checker (importable and CLI).

## References

- `references/spec-schema.md` — the canonical spec shape all eight stages contribute to.
- `references/red-dot-system.md` — the full system description.

---
**Final stage.** Back to the [router](../SKILL.md).