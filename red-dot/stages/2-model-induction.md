
# Red Dot - Model Induction (Stage 2)

> **Stage 2 of 8 — Red Dot pipeline.**
> ← prev: [case intake](1-case-intake.md)  ·  next: [outcome space](3-outcome-space.md) →
> Shared nodes: [the gate machinery](../concepts/the-gates.md), [spec schema](../concepts/spec-schema.md)

Seed, then render the draft deliberately wrong *(interview mode only — see the mode gate below)*. Turn the case bank into a lifecycle map and a stuck-map. The expert need only be a recognizer, not a world-builder: show a correctable draft and harvest the correction.

## Contract

- **Consumes:** the case bank (Stage 1) and the positioning brief (Stage 0).
- **Produces:** the lifecycle_model (5 stages, rarely 6) and the stuck_map (transition failures by boundary, typed by locus).
- **Owes the rest of the system:** every stage boundary maps to something in the offer (commercial closure); every stuck point is later detectable by a question (Stage 4).

## Method

> **Mode gate (read [the router](../SKILL.md) §"Operating mode" first).** Steps 1–2
> below describe **interview mode**, where a live expert corrects a wrong draft.
> In **brief-only mode** (no interview — the expert wrote their perspective and the
> skill builds unattended) the deliberate-wrongness has no one to correct it and
> only degrades the model: **skip it.** Build the most accurate lifecycle_model and
> stuck_map you can from the brief, and route every joint you had to *infer* (not
> read directly) to §7 of the design doc so the expert can correct it later. The
> rest of the method — cutting stages at value-joints (3), the stuck_map (4), the
> craft rules, and the acceptance test — applies unchanged in both modes.

1. **Seed a draft from anywhere** — the cases, adjacent experts, public
   literature.
   - *Interview mode:* then deliberately render it WRONG in a correctable way:
     right vocabulary but wrong joints, right stages but wrong order, right
     stuck-point but wrong cause. Calibrate the wrongness: too wrong and they
     dismiss it; too right and they rubber-stamp it. The wrong draft is
     scaffolding shown to the expert — it is **never** written to `spec.json`.
   - *Brief-only mode:* skip the wrongness. Write the most accurate model the
     brief supports straight to the spec; send low-confidence inferences to §7.
2. **Let correction do the eliciting** *(interview mode only)*. 'No, you've got
   the mechanism backwards, it's actually...' is the expert reaching past their
   espoused theory. The cases they grab while correcting ('take Sarah, she was
   past that and still stuck') flow back into the case bank. (In brief-only mode
   there is no correction turn; §7 carries the same uncertainty forward instead.)
3. **Cut stages at the joints where the expert adds value** (from the brief).
   Each stage carries BOTH faces: the new problem-surface that appears, and the
   mastery that deepens. Name each stage so a person will say it out loud
   ('I'm a ___'); naming is its own design step.
4. **Build the stuck_map** as transition failures at boundaries, each tagged
   symptom / cause / misdiagnosis and typed by LOCUS:
   capability hole / capability currency / value collapse / segment-and-courage.
   Loci are depth-ranked; the deepest active one gates the rest. Tenure is a
   prior over locus (short -> hole; mid -> currency; long -> value/courage).

## Craft rules and failure modes

- A 6th stage is justified only by a REGIME CHANGE (the capability curve resets
  and experienced people get demoted in effectiveness). Otherwise 5.
- Prune impossible cells (e.g. value-collapse before any value delivered). The
  map of the impossible is as much expertise as the cells you fill.
- **Acceptance test is not 'do you like this map'** — a flattering map earns a
  yes whether or not it's true. The test is: 'does this map drop your real
  clients (Stage 1 cases) where you would?' Run the cases through it.
- **Brief-only guard.** Treat 'render it wrong' as inert when no expert is in the
  loop. Writing a deliberately-wrong lifecycle_model or stuck_map to `spec.json`
  is a defect, not the method — the method's *output* is always the accurate
  model; wrongness only ever lived in the draft a human was about to fix.

## Output — what you write into `spec.json`

```
spec.lifecycle_model = {"stages": [
  {"id":"s1","name":"...","problem_face":"...","mastery_face":"...","tenure_hint":"..."},
  ... up to 5 (rarely 6)
]}
spec.stuck_map = [
  {"id":"sp1","boundary":"s1->s2","locus":"capability_hole",
   "symptom":"...","cause":"...","misdiagnosis":"...","detected_by":[]},
  ...
]
```
Leave `detected_by` empty; Stage 4 fills it with question ids.

## Gates this stage must satisfy

- **Detectability** (activates at assembly once a stuck_map exists): every stuck
  point must be detectable by at least one question. You set this up here.
- **Two-faced coverage**: both faces of each stage must end up represented in
  the instrument — record both faces now so Stage 4 can cover them.
- **Commercial closure**: every boundary maps to an offer.

---
**Next stage:** [outcome space](3-outcome-space.md). Back to the [router](../SKILL.md).