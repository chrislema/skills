
# Red Dot - Content Authoring (Stage 6)

> **Stage 6 of 8 — Red Dot pipeline.**
> ← prev: [scoring](5-scoring.md)  ·  next: [assembly](7-assembly.md) →
> Shared nodes: [the kit — author the pairwise](../concepts/the-kit.md), [the gate machinery](../concepts/the-gates.md), [spec schema](../concepts/spec-schema.md)
> Relies on upstream: [the address set](3-outcome-space.md), [the stuck_map and stages](2-model-induction.md) — if missing, go there first.

Write each atom against the address that selects it, never beyond. The report reads as one continuous piece written to this person, but it is assembled from authored layers and one deterministic step. Flow, interaction, and uniqueness are all handled here at design time.

## Contract

- **Consumes:** the address schema, lifecycle_model, stuck_map, and voice/banned-phrase constraints.
- **Produces:** an authored landing for every reachable address: skeleton + atoms + interaction cells + variant banks.
- **Owes the rest of the system:** coverage, the honesty gate, the voice gate, and claim-to-input binding on every assertion.

## Method

- **The fixed skeleton carries the flow.** Author the report's arc once (why this
  exists -> why your situation is the advantage -> the live problem -> what
  becomes possible -> where to point first -> the shadow to watch -> the close).
  Every transition is authored into the scaffold; scoring only decides which
  atoms drop into the slots.
- **The atom library fills the slots.** Stage shells (one per stage, with
  end-asymmetry baked in: stage 1 validates before it gaps; the top stage asks
  for referrals, not a purchase), theme/locus modules, interaction cells (the
  'because you're an A and your top driver is B' lines), and variant banks (two
  or three phrasings per atom, selected by a stable per-session hash).
- **Author at the level of intent, not implementation.** 'Establish a reliable
  outreach rhythm' is durable; 'use [tool] to draft three messages Monday' dates.
  Keep tool-level how-to in a thin, clearly-dated optional annotation if at all.

## Craft rules and failure modes

- **Claim-to-input binding.** Assert only what was scored. The quiet failure is
  unmeasured HISTORY ('you've drifted from', 'you stopped') — it reads as insight
  and rests on nothing the instrument measured. Reframe unmeasured mechanisms as
  positional-typical ('where people in this spot usually feel it'), not fact.
- **Voice gate.** Banned phrases and internal jargon never reach the customer.
  The banned family includes 'here's the thing...', 'the part nobody says out
  loud', 'here's what [X] can't tell you'. Lint every variant, not just the first.
- **Honesty gate.** Not every path may land on 'you need my thing'. Validate-first
  cells validate; the top stage refers. A rigged map runs the authority transfer
  in reverse.

## Output — what you write into `spec.json`

```
spec.content = {
  "quadrants": {"<addr-component>": {"name":"...","gap_family":"...",
      "validate_first":false, "opener":["variant 1","variant 2"],
      "body":["para","para","para"]}, ...},
  "depthLeads": {"<full-address-key>": "one backed sentence per address", ...}
}
```
Compose openers + depth-lead + body per address. Include ALL variants so the
gate-checker lints every phrasing a user could see.

## Gates this stage must satisfy

- **Coverage**: every reachable address has an authored landing.
- **Evidence**: every claim backed by a scored input; no unmeasured-history claims.
- **Voice gate** and **Honesty gate** as above. All enforced at assembly; author
  to pass them.

---
**Next stage:** [assembly](7-assembly.md). Back to the [router](../SKILL.md).