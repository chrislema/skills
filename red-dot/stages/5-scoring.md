
# Red Dot - Scoring Spec (Stage 5)

> **Stage 5 of 8 — Red Dot pipeline.**
> ← prev: [instrument](4-instrument.md)  ·  next: [content](6-content.md) →
> Shared nodes: [the gate machinery](../concepts/the-gates.md), [spec schema](../concepts/spec-schema.md)
> Relies on upstream: [the address schema](3-outcome-space.md) — if missing, go there first.

A total function to an address. The scorer's job is to resolve every possible answer pattern to a valid, fully-specified address — and to produce that address, not a fuzzy result an interpreter softens later.

## Contract

- **Consumes:** the instrument (Stage 4) and the address schema (Stage 3).
- **Produces:** a deterministic map from answer pattern to address, computing the gaps along the way.
- **Owes the rest of the system:** totality (every pattern resolves) and bijection-readiness (never emit an address Stage 6 didn't author).

## Method

Finalize the scoring rule that turns answers into an address. For the two-strand
quadrant reference: sum each axis, place the quadrant by threshold, then fork the
within-cell band on the dimension that actually varies (shared altitude for
on-diagonal cells, gap magnitude for off-diagonal). The address is the fully
resolved coordinate (e.g. quadrant x band), and several of its components ARE
gaps (the normative gap = stage vs tenure; any correlational gaps between
strands).

Then VALIDATE with the bundled script:

```bash
python scripts/validate_scoring.py spec.json
```

It enumerates the entire reachable address space (so you catch dead cells and
addresses reachable in theory but never in practice) and runs the **exemplar
test**: add a few people whose answer you already know and confirm the math
lands them right. That is the poor-man's validation, and it catches scoring bugs
nothing else will.

## Craft rules and failure modes

- **Be total.** Every answer pattern must resolve to a valid address. The
  validator will tell you if any pattern falls through.
- **Don't derive the depth read from the same scores that drew the quadrant** —
  that makes the two outputs correlated by construction and the second one stops
  adding information. Fork depth on an independent or genuinely-varying quantity.
- Add exemplars to the spec so the test is repeatable across iterations.

## Output — what you write into `spec.json`

```
spec.scoring = {            # the two-strand-quadrant reference shape
  "quadrant": {"threshold": 3.0},
  "bands": {"aligned": {"measure":"mean","cut":4.0,"high":"...","low":"..."}, ...}
}
spec.exemplars = [{"name":"obvious stage-2 Bob","self":1.8,"team":4.1,"expect":"martyr"}, ...]
```
For a richer address schema, generalize the resolver and the validator's
reachability enumeration accordingly.

## Gates this stage must satisfy

- **Coverage / Bijection** readiness: the reachable set the validator prints
  must equal the addresses Stage 6 authors. Hand that set to Stage 6.
- Owns the **exemplar test** as a standing check.

---
**Next stage:** [content](6-content.md). Back to the [router](../SKILL.md).