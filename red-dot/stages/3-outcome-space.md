
# Red Dot - Outcome-Space Design (Stage 3)

> **Stage 3 of 8 — Red Dot pipeline.**
> ← prev: [model induction](2-model-induction.md)  ·  next: [instrument](4-instrument.md) →
> Shared nodes: [the kit — choosing the gap](../concepts/the-kit.md), [the gate machinery](../concepts/the-gates.md), [spec schema](../concepts/spec-schema.md)

Choose the gap, then set the resolution. This is the most consequential single choice in the whole build, because it sets what the report can honestly say. Two coupled jobs: pick the gap and its benchmark, and design the address every respondent resolves to.

## Contract

- **Consumes:** the lifecycle_model and stuck_map (Stage 2).
- **Produces:** the address schema (the coordinate every respondent resolves to) and the chosen gap with its benchmark source.
- **Owes the rest of the system:** the exact set of addresses that must have authored landings (Stage 6) and the list of things that must be discriminable (Stage 4).

## Method

**Job 1 - choose the gap and source its benchmark.** A gap compares the
respondent's answer to a benchmark they don't control. Pick the family whose
geometry fits:
- **Normative** — where tenure/stage says you should be vs. where you operate.
  The cleanest, because half of it (time served) is not a self-assessment.
- **Predictive** — where a model said you'd struggle vs. where you do.
- **Correlational** — where two of your own answers should track but diverge
  (e.g. the three-tense spread, or a capability vs. its consequence).

Match the family to the cell. A correlational gap needs DIVERGENCE, so a
both-agree cell (both axes high or both low) has near-zero correlational gap and
needs a normative one — or must be a declared validate-first cell that doesn't
manufacture a gap. Never lean on an UNMEASURED implied benchmark; that is a
self-rating in disguise and the gate will reject it.

**Job 2 - the resolution dial.** Design the address (e.g. stage x locus x
theme x gap-state). Set granularity by recognition: fork only where the READER
would feel the difference, or wherever the EXPERT would give different advice.
The cheapest way to add real resolution is to fork on what scoring already
computes (the gap, the level, the weakest axis) rather than measuring more. And
never let the visualization out-resolve the prose: if the dot is plotted finely
but the report forks coarsely, the reader feels the seam.

## Craft rules and failure modes

- This stage is where most downstream failures originate, and they surface far
  away (an over-resolved address becomes a coverage/bijection failure at Stage 7).
- Declare every reachable address key now. Stage 6 must author a landing for
  each; the bijection gate checks the two sets are equal.
- If you reuse the two-strand quadrant primitive (two axes whose ideal is
  'both high'), the four cells name themselves; add an INDEPENDENT depth read so
  the second output isn't correlated-by-construction with the quadrant.

## Output — what you write into `spec.json`

```
spec.gap = {"family": "correlational|normative|predictive", "benchmark": "..."}
spec.axes = {"axisA": {"items": N}, "axisB": {"items": M}}
spec.scoring = { ...address-schema params: thresholds, band cuts... }
# plus the enumerated reachable address keys, or the rule that generates them
```
The bundled scripts (Stage 5/7) implement the two-strand-quadrant pattern as a
working reference; for a richer address schema, generalize the resolver.

## Gates this stage must satisfy

- **Gap present**: every address leverages a measured gap OR is a declared
  validate-first cell; none leans on an unmeasured implied benchmark.
- **Coverage / Bijection**: the reachable address set you declare here is the
  exact set Stage 6 must author and Stage 7 will verify.

---
**Next stage:** [instrument](4-instrument.md). Back to the [router](../SKILL.md).