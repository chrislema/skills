
# Red Dot - Case Intake (Stage 1)

> **Stage 1 of 8 — Red Dot pipeline.**
> ← prev: [positioning](0-positioning.md)  ·  next: [model induction](2-model-induction.md) →
> Shared nodes: [spec schema](../concepts/spec-schema.md)

The concrete past-tense walk, fenced from abstraction. Get real client cases out of the expert without letting anyone (expert or you) jump to the framework. The cases become the raw material the map is induced from and the scoring is calibrated against.

## Contract

- **Consumes:** the positioning brief plus raw seed (the expert's posts, notes, talks, real clients).
- **Produces:** a bank of real client cases, each tagged symptom-observed / cause-actual / misdiagnosis / where-they-landed.
- **Owes the rest of the system:** cases that are concrete, past-tense, and UNTYPED — no stage labels. The moment intake emits a stage, it has started leading the witness.

## Method

Walk real clients one at a time using Critical-Decision-Method probes:
- Take one specific client. What did you NOTICE first? (the symptom they showed)
- What was ACTUALLY going on underneath? (the cause they couldn't see)
- What would a novice practitioner have thought was wrong? (the misdiagnosis)
- What happened next? Where did they end up?

Then: next client. Keep it past-tense and concrete. You are collecting events,
not opinions. If the expert starts theorizing ('well, clients generally go
through three phases...'), gently redirect to a specific person and a specific
moment. Recognition over generation: the abstraction comes in Stage 2.

## Craft rules and failure modes

- **Leading the witness is the default failure, not an occasional slip.** Stay
  fenced: concrete, past-tense, case-local. Do NOT propose a category, stage, or
  pattern. The clustering into stages happens in a separate later pass.
- Asking for the abstraction yields the tidy, rationalized, wrong answer. Asking
  for cases yields the theory-in-use.
- Aim for enough cases to span the domain (8 to 15 is usually plenty), including
  a few where the expert was surprised or the obvious read was wrong.

## Output — what you write into `spec.json`

```
spec.cases = [
  {"id": "c1", "situation": "...", "symptom": "...",
   "cause": "...", "misdiagnosis": "...", "where_landed": "..."},
  ...
]
```
Design-time only — cases are not shipped to runtime, but they stay in the spec
so Stage 2 can induce from them and Stage 5 can calibrate against them.

## Gates this stage must satisfy

- No gate fires here directly; this is a process fence. Its downstream symptom,
  an ungrounded map, is caught by the case-grounded acceptance test in Stage 2.
- Keep the cases honest and specific; they are the stress set for everything
  downstream.

---
**Next stage:** [model induction](2-model-induction.md). Back to the [router](../SKILL.md).