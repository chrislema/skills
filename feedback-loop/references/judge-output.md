# Judge Output (Phase 2 result)

The scored result Phase 2 returns. The contract: `to_reach_next` contains an entry for every dimension scored below `scale.max` and every failed gate — a sub-max score with no matching entry is an error.

## Schema

```json
{
  "_meta": {
    "judged_artifact": "what was graded",
    "inputs_used": ["primary artifact", "any secondary surface used"],
    "judge_rubric": "which rubric was applied",
    "independence_note": "present if the grader also authored the rubric this session"
  },
  "gates": [{ "id": "gate_id", "passed": true, "evidence": "<quoted span>" }],
  "dimensions": [{ "id": "dimension_id", "score": 4, "evidence": "<quoted span>", "reasoning": "<one sentence>" }],
  "not_scored": ["<dimension whose required surface was absent>"],
  "to_reach_next": [
    { "id": "dimension_or_gate_id", "current": 3, "target": 4,
      "delta": "<specific change, phrased against the artifact>",
      "owner": "<stage or section that owns the fix>",
      "fix_type": "local | upstream-structural | tier-ceiling",
      "honesty_note": "<only when raising the score means expanding scope or gaming; else null>" }
  ],
  "weighted_avg": 0.0,
  "overall": 0.0,
  "caps_applied": ["<gate id or none>"]
}
```

`fix_type` is the routing signal: `local` = actionable now, `upstream-structural` = fix an earlier stage, `tier-ceiling` = scope decision not a defect. `not_scored` dimensions are excluded from the weighted average and the rest renormalized — don't guess a score for a surface you couldn't see.

## Worked example (real run against red-dot's reference assessment)

The Alignment Mirror, compiled from red-dot's bundled example spec, scored 0.85. All gates passed; three dimensions came in below max and each routed differently — one `local` copy edit, one `local` content authoring, and one `tier-ceiling` whose honesty_note tells the caller *not* to chase it.

```json
{
  "_meta": {
    "judged_artifact": "The Alignment Mirror (compiled from red-dot example spec)",
    "inputs_used": ["assessment.html", "design.md"],
    "judge_rubric": "red-dot-assessment-rubric.json"
  },
  "gates": [
    { "id": "honesty_substantive", "passed": true, "evidence": "on-diagonal results validate instead of gapping; no path funnels to the offer" },
    { "id": "no_unmeasured_history", "passed": true, "evidence": "copy is present-tense and answer-grounded" },
    { "id": "voice_spirit", "passed": true, "evidence": "plain second-person voice; no guru-voice family" }
  ],
  "dimensions": [
    { "id": "gap_choice_and_benchmark_honesty", "score": 5, "evidence": "off-diagonal headline a correlational gap; on-diagonal decline to manufacture one", "reasoning": "gap against a fixed point the respondent doesn't control where divergence exists" },
    { "id": "behavior_not_self_report", "score": 4, "evidence": "mostly events; q5/q7 lean introspective", "reasoning": "strong behavioral design, two introspective items remain" },
    { "id": "result_lands_on_the_respondent", "score": 4, "evidence": "per-quadrant body + per-band depth lead", "reasoning": "reads written-to-you but body shared across both bands of a quadrant" },
    { "id": "resolution_matched", "score": 5, "evidence": "dot plotted from exact means; never out-resolves prose", "reasoning": "resolution deliberately matched" },
    { "id": "non_repetition_across_paths", "score": 3, "evidence": "4 quadrant bodies, no interaction cells", "reasoning": "real but bounded variation" },
    { "id": "naming_is_sayable", "score": 5, "evidence": "The Lone Athlete / The Servant Martyr / The Grinder / The Aligned Operator", "reasoning": "memorable say-out-loud names" }
  ],
  "not_scored": [],
  "to_reach_next": [
    { "id": "behavior_not_self_report", "current": 4, "target": 5, "delta": "rewrite q5 and q7 to elicit an observable event instead of internal noticing", "owner": "Stage 4 - instrument", "fix_type": "local", "honesty_note": null },
    { "id": "result_lands_on_the_respondent", "current": 4, "target": 5, "delta": "author a distinct body per address (8) instead of one shared across both bands, each ending in one named highest-leverage next move", "owner": "Stage 6 - content", "fix_type": "local", "honesty_note": null },
    { "id": "non_repetition_across_paths", "current": 3, "target": 4, "delta": "add a theme/interaction dimension to the address schema so combinations resolve to distinct reads via interaction cells", "owner": "Stage 3 - outcome-space, cascading to Stage 6", "fix_type": "tier-ceiling", "honesty_note": "A 3 is correct for a deliberately coarse Tier-0 mirror. Raising it is a scope decision (climb to Tier 1), not a copy fix; don't chase it unless you want the larger instrument." }
  ],
  "weighted_avg": 4.39,
  "overall": 0.85,
  "caps_applied": ["none"]
}
```

The shape to copy: actionable fixes name their owning stage and can be made now; the one that can't told the caller the honest truth that its score is a scope decision — the difference between improving the instrument and gaming the number.
