# The Gates — invariants on the seams

Validation is not a final step; it is a standing checker wired onto the seams,
run before any artifact is emitted. It is enforced mechanically at
[assembly](../stages/7-assembly.md) by `scripts/gate_check.py` (and the engine's
`--check` mode). Every stage's "owes" clause maps to one of these.

Gates carry one of three severities:

- **BLOCK** — must pass or the assembler refuses to emit.
- **ADVISORY** — reported every run, non-blocking at the current tier, tracked.
- **N/A** — not applicable until the spec gains the structure the gate checks.

## Blocking gates

| Gate | Asserts | Catches |
|---|---|---|
| Coverage | every reachable address has an authored landing | over-resolution; orphan scores |
| Bijection | reachable addresses equal authored landings | scoring/content drift |
| Gap present | every address leverages a measured gap OR is a declared validate-first cell; none leans on an unmeasured implied benchmark | nothing to motivate movement; a self-rating in disguise |
| Evidence | every claim backed by a scored input; no unmeasured-history claims | content asserting beyond what was measured |
| Voice gate | banned phrases never reach the customer | the "here's the thing" / "nobody talks about" family |
| No orphan questions | every question feeds the stage axis or a named theme | instrument padding |
| Honesty gate | no path is forced to conclude "buy the thing" | a rigged map |

## Three refinements worth knowing

1. **The gap-present gate encodes the commercial asymmetry.** Not every cell must
   be gapped. A both-low / early cell is the validate-first analog of stage 1 —
   you validate and stabilize, you do not manufacture a gap, and you never assert
   a "you should be further" baseline you didn't measure.
2. **The evidence gate includes a temporal-claim lint.** The common drift is not
   invented statistics but quiet history ("you've drifted from", "you stopped").
   A standing lint catches the class; inspection misses it case by case.
3. **The checker is tier-aware.** Detectability, commercial closure, two-faced
   coverage, ranking-gap-derived, and positional rationale are N/A until the
   spec contains a stuck_map, an offer, maturity stages, or a ranking — then they
   activate as BLOCK. Severity keys off spec presence, not a tier flag.

Back to the [router](../SKILL.md).
