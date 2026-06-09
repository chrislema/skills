
# Red Dot - Instrument Authoring (Stage 4)

> **Stage 4 of 8 — Red Dot pipeline.**
> ← prev: [outcome space](3-outcome-space.md)  ·  next: [scoring](5-scoring.md) →
> Shared nodes: [the kit — the three-tense pattern](../concepts/the-kit.md), [the gate machinery](../concepts/the-gates.md)
> Relies on upstream: [the stuck_map it must detect](2-model-induction.md), [the address schema](3-outcome-space.md) — if missing, go there first.

Ask the symptom, hide the rung. Author 10 to 15 questions that place the dot and read the secondary themes. The length itself is a trust signal: short enough that completion stays high, long enough that the result feels earned.

## Contract

- **Consumes:** the address schema (what must be told apart) and the stuck_map (what must be detectable).
- **Produces:** 10 to 15 questions, each tagged to the axis/theme it feeds, behaviorally concrete, options in rung order.
- **Owes the rest of the system:** every stuck point detectable by at least one question; no orphan questions; both faces of each stage represented.

## Method

Author questions against the address schema. Two question types usually appear:
stage-placement questions (discriminate adjacent stages, the primary axis) and
theme questions (read a few sub-dimensions, the report's texture).

Reach for the **three-tense pattern** (have-done / doing-now / do-consistently)
whenever 'do they do this reliably, or did they once' is the diagnostic
question. It operationalizes behavioral elicitation, yields a correlational gap
for free (the tenses must cohere; their spread is a within-respondent
benchmark), and reads maturity as consistency with no self-rating.

If tenure is a prior over locus, the instrument can BRANCH: place stage and
tenure first, then serve locus-discriminating questions conditioned on that
prior. Flat is simpler; branching is sharper and shorter-feeling. Choose per
domain.

## Craft rules and failure modes

- **Never ask people to rate the variable.** They can't perceive the thing being
  measured (that's why they need the expert). Ask about concrete, observable
  symptoms and let the scoring infer the stage/locus.
- **Kill social desirability.** If one option is visibly 'the good answer',
  everyone picks it and the gap collapses. Make every option a legitimate mode;
  give the high-alignment option a real cost so it isn't the trophy. Forced
  choice between equally-attractive options often discriminates better than
  agree/disagree scales. (Per-session option SHUFFLE, added at assembly, kills
  the POSITION cue; this rule kills the CONTENT cue.)
- **Behaviorally concrete, not Likert-vague.** 'Last time this happened, I did
  X / did Y' beats 'I sometimes feel prepared'. Options in rung order map to the
  ladder of progress, where the next rung up is the prescription.

## Output — what you write into `spec.json`

```
spec.questions = [
  {"id":"q1","axis":"axisA","behavioral":true,"content_cue":false,
   "stem":"...","options":["worst ... ","...","...","...","best ..."]},
  ...
]
```
Option order in the data is rung order (value = index + 1); display is shuffled
at assembly. Tag each question's axis/theme. Fill `detected_by` on the
stuck_map entries this question detects. Optionally add `reads` (a short label of
what the item measures) and `catches` (the failure mode it detects); these feed
the design document at Stage 7 and are ignored by the engine.

## Gates this stage must satisfy

- **No orphan questions**: every question feeds the stage axis or a named theme.
- **Behavioral elicitation** (advisory): each question should produce a
  benchmarkable observation, not a self-rating of an inner state. Introspective
  items are flagged, not forbidden — minimize them.
- **Detectability / Two-faced coverage**: cover every stuck point and both faces
  of each stage.

---
**Next stage:** [scoring](5-scoring.md). Back to the [router](../SKILL.md).