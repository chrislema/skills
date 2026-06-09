---
name: feedback-loop
description: Author an automated evaluation rubric for any prompt or skill, apply it to real outputs, and return scores plus actionable improvement feedback — closing the loop between "what good looks like" and "how to get there." Use this whenever someone wants to grade, score, evaluate, QA, or measure the outputs of a prompt/agent/skill; build an evaluator, scorecard, rubric, or LLM-as-judge; set acceptance criteria for an agent; run the judge on a concrete output; or asks "how would I know if this is doing a good job", "score this output", "what would get this to a 4", or "evaluate this and tell me how to improve it". Trigger it even when the word "rubric" isn't used — any request to systematically judge the quality of what a prompt, agent, or skill produces, or to improve an output against such a judgment, is in scope. Handles both prompts and skills.
---

# Feedback Loop

One skill, two halves, and the loop between them:

- **Phase 1 — Author** a rubric for a target prompt or skill: scored dimensions, pass/fail gates, anchored guidance, an aggregation formula, and a judge prompt that applies it.
- **Phase 2 — Apply** that rubric to a real output and return a scored result that **always carries improvement feedback** — for every dimension below max and every failed gate, the specific change that would raise it and where that fix lives.
- **The loop** — feed the feedback back into the target, regenerate, re-grade, confirm movement. Stop when what remains is a scope decision for a human, not a defect.

## The governing idea

The naive way to build a rubric is to read the target's output template and make one dimension per section. That grades the *shape of the artifact* while ignoring the *behavior and intent* the prompt actually cares about — and silently inherits every blind spot in the source. A planner that says "ask only blocking questions, prefer inference, ship the smallest real slice" has none of those in its output template, so a shape-only rubric never measures the rules that make it distinctive. Worse, an agent that should have asked but instead guessed scores *well* on "states its assumptions" while doing the wrong thing.

So the rule that governs both phases: **grade what the target is trying to make happen, not just the format it emits — and when you give feedback, improve the instrument, not the number.**

## Routing

Decide which phase the request needs by what was supplied:

- Given a **prompt or skill** and asked to evaluate/score/QA it, with **no rubric yet** → start at **Phase 1**, then offer Phase 2.
- Given a **rubric and a concrete output** → go straight to **Phase 2**.
- Asked to **improve an output until it's good**, or given a target plus example outputs → run the **full loop** (Phase 1 once, then Phase 2 each iteration).

If asked to score but there's no rubric, author one first (Phase 1) — don't grade against criteria you never wrote down. If asked to author but the output to be graded doesn't exist yet, that's fine; Phase 1 doesn't need a sample output, only the target.

---

## Phase 1 — Author the rubric

**1. Identify the target.** Prompt (pure behavior) or skill (behavior + a triggering description + maybe scripts)? A skill has an extra axis a prompt doesn't — does it fire when it should and stay quiet when it shouldn't — so give triggering its own dimension or note it needs its own rubric. Read the full source; don't skim to the output template, that's the trap.

**2. Extract requirements into four buckets.** Each maps to a different rubric element:
- *Behavioral rules* — how the target should act ("ask only blocking questions," "smallest slice first"). Most commonly missed, often most important; hunt for them.
- *Output/structure requirements* — the shape of the deliverable.
- *Hard constraints / must-nots* — bright-line prohibitions.
- *Vague quality goals* — adjectives with no built-in test ("concrete," "reviewable"). Operationalize these or the judge fills the vacuum with vibes.

**3. Gate vs. graded — for each requirement, ask "can I describe a believable middle score?"** If yes → a graded dimension. If a middle is incoherent (you either claimed a tool you don't have or you didn't) → a gate. Putting a binary requirement on a 1–5 scale is the main source of run-to-run noise. Gates sit outside the weighted sum and veto or cap the score.

**4. Write graded dimensions with concrete anchors.** For each, describe what a 1, 3, and 5 look like in terms of evidence visible in the output. Avoid "somewhat good / good / great" — anchor to specifics. Anchors are also what make Phase 2's feedback actionable later, so a vague anchor is a vague fix waiting to happen.

**5. Detect "rules with no home."** Cross-check every behavioral rule against where it would actually show up. If a rule can't be observed in the surface the rubric grades, either point the dimension at the right surface (grade the conversation, not just the artifact) or flag it as unmeasurable and say what would need to be captured. Never silently drop it — these are disproportionately the rules that define intent.

**6. Assign weights with discipline.** Heaviest dimension = the one whose failure most defines a bad output (say why). Cap or omit any catch-all "general quality" dimension — it's unanchored and the biggest source of noise. Gates carry no weight. Keep it to ≈4–8 dimensions.

**7. Define scoring with the floor subtracted.** `overall = (weighted_avg − min) / (max − min)`, so an all-minimum output maps to 0, not the middle of the range. Without it, scores compress and stop discriminating. Then specify gate caps (critical → 0; minor → 0.5).

**8. Verify with two exemplars.** Write a short known-good and known-bad output and score both. The good lands high; the bad trips gates or lands low. If the rubric can't separate them, tighten anchors or convert a fuzzy dimension to a gate.

**9. Emit three artifacts** (see `references/rubric-formats.md` for exact templates): the human-readable rubric, the machine-readable JSON, and the judge prompt — and the judge prompt **must** include the `to_reach_next` improvement contract so its outputs are improvable, not just scored.

---

## Phase 2 — Apply the rubric and give feedback

**Gather inputs:** the rubric (from Phase 1 or supplied), the output(s) to grade, optionally the input/task for context, and any secondary surface the rubric flags as needed (`needs_design_doc` and the like — e.g. non-repetition is invisible on a single rendered result; a benchmark's source may only live in a design doc). If a required surface is missing, score what you can and mark the rest `not_scored` — never guess. You grade an output the caller supplies; you don't build the output yourself.

**1. Gates first.** Pass/fail each, quoting the exact span that decides it. No evidence that a required property holds → treat as failing; don't assume good faith.

**2. Score each dimension** against its anchors, quoting a span as evidence for every score. Evidence absent → score low, don't infer intent. Scoring without a quoted span is how judges drift into global impressions.

**3. Aggregate** over scored dimensions with the floor-subtracted formula, then apply the lowest gate cap that fires.

**4. Improvement feedback — the core, and non-optional.** Hard rule: **every dimension below max and every failed gate gets a `to_reach_next` entry.** A sub-max score with no feedback is a bug. Each entry carries:
- **delta** — the specific change, phrased against *this artifact*, not the anchor ("rewrite q5/q7 as event questions," not "be more behavioral").
- **owner** — where the fix lives (the stage for a pipeline, the section for a prompt), so the caller can route it.
- **fix_type** — `local` (a copy edit now), `upstream-structural` (change an earlier stage's output), or `tier-ceiling` (can't rise without expanding scope — a decision, not a defect).
- **honesty_note** — only when raising the score would mean expanding scope or gaming the rubric.

**5. Don't optimize the number instead of the output.** Some scores are correct for the chosen scope; a deliberately coarse artifact *should* score modestly on richness dimensions. Flag every `tier-ceiling` item as a human scope decision. If you authored the rubric earlier this same session, say so — grading your own criteria isn't an independent check.

See `references/judge-output.md` for the output schema and a full worked example.

---

## The loop

When the goal is to actually improve an output, iterate:

1. Run Phase 2 → get `to_reach_next`.
2. Apply the `local` fixes to the target's source; route `upstream-structural` ones to the owning stage.
3. Regenerate the output and re-run Phase 2.
4. Confirm the targeted dimension moved **and** nothing else regressed.
5. Stop when the only gaps left are `tier-ceiling` — those go to a human, not another iteration.

Two guards on the loop, because a closed automated loop tends to satisfy the judge rather than the end user: keep a human on the `tier-ceiling`/scope calls, and don't let the same model author the rubric, judge against it, and apply the fixes in one unbroken automated cycle — run the judge as a separate pass (ideally a different model or session) so the scores stay honest. The loop's job is a better instrument, not a higher number.

## Tone with the user

Lead with what the rubric surfaces that they couldn't easily get themselves — the "rules with no home," the binary-on-a-scale fixes, and in Phase 2 the `local` fixes they can act on now (kept separate from the scope decisions). Don't bury those under boilerplate. If something genuinely can't be measured from outputs alone, say so rather than inventing a dimension that pretends to.
