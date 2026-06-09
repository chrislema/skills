# Rubric Formats (Phase 1 output)

The three artifacts Phase 1 emits. Follow these so the rubric is consistent and machine-parseable, and so the judge prompt is directly runnable in Phase 2.

## 1. Human-readable rubric (`<name>-rubric.md`)

```markdown
# Rubric: <target name>

**Target type:** prompt | skill
**What it grades:** outputs the target produces (and, for skills, whether it triggers correctly)
**Scale:** dimensions 1–5 · overall normalized to 0–1

## Gates (pass/fail — evaluated before scoring)
| Gate | Check | Severity | On fail |
|------|-------|----------|---------|
| <id> | <what makes it pass> | critical | overall → 0 |
| <id> | <what makes it pass> | minor | overall capped at 0.5 |

## Dimensions
| Dimension | Weight | 1 | 3 | 5 |
|-----------|:------:|---|---|---|
| <id> | 10 | <anchor> | <anchor> | <anchor> |
(Weight rationale: <why the heaviest is heaviest>)

## Scoring
weighted_avg = Σ(weight·score) / Σ(weight)
overall = (weighted_avg − 1) / 4        # floor-subtracted: 1→0, 5→1
Apply gate caps after.

## Exemplars (discrimination check)
**Known-good (≈ high):** <short example>
**Known-bad (trips gates / low):** <short example>

## Unmeasurable rules (flagged, not dropped)
- <rule> — not observable from the output alone; would require capturing <surface>.
```

## 2. Machine-readable rubric (`<name>-rubric.json`)

```json
{
  "target": { "type": "prompt", "name": "...", "source_summary": "..." },
  "scale": { "min": 1, "max": 5 },
  "gates": [
    { "id": "...", "description": "...", "severity": "critical", "on_fail": "cap", "cap_value": 0.0 }
  ],
  "dimensions": [
    { "id": "...", "weight": 10, "description": "...",
      "anchors": { "1": "...", "3": "...", "5": "..." },
      "needs_design_doc": false }
  ],
  "aggregation": {
    "method": "weighted_normalized",
    "formula": "(sum(weight*score)/sum(weight) - scale.min) / (scale.max - scale.min)",
    "gate_handling": "Apply gate caps after normalization; lowest applicable cap wins."
  },
  "output_range": [0.0, 1.0]
}
```
Notes: `severity` is `critical`|`minor`; `on_fail` is `cap` (with `cap_value`) or `veto`. Mark any dimension that can't be scored from the primary artifact with `needs_design_doc: true` (or a named secondary surface) — Phase 2 reads this. For a skill, add a `triggers_appropriately` dimension or gate.

## 3. Judge prompt (`<name>-judge.md`)

The prompt run in Phase 2. It takes the target's task and output and returns scored JSON. Fill the brackets from the rubric.

```markdown
You are an evaluation judge. Score a single output of <target> against the rubric below. Be strict and evidence-driven — discriminate good from bad, don't be charitable.

## You receive
- TASK: the input given to the target.
- OUTPUT: what the target produced. [+ any secondary surface the rubric flags as needed]

## How to judge
1. Gates first: pass/fail each, quote the deciding span. No evidence a required property holds → fail.
2. Score each dimension 1–5 by its anchors, quoting a span as evidence. Evidence absent → score low. If a needs_design_doc dimension's surface wasn't provided, mark it not_scored and renormalize.
3. Compute the overall, then apply gate caps.

## Gates
[id — check — severity — cap]

## Dimensions
[id (weight) — 1/3/5 anchors]

## Scoring
weighted_avg = sum(weight*score)/sum(weight over scored)
overall = (weighted_avg - 1) / 4
Apply the lowest gate cap that fires.

## Improvement feedback (required)
For every dimension below 5 and every failed gate, emit a to_reach_next entry: delta (specific change against the artifact), owner (stage/section that owns the fix), fix_type (local | upstream-structural | tier-ceiling), honesty_note (only if raising the score means expanding scope or gaming the rubric).

## Return exactly this JSON, nothing else
{
  "gates": [{ "id": "...", "passed": true, "evidence": "<span>" }],
  "dimensions": [{ "id": "...", "score": 4, "evidence": "<span>", "reasoning": "<one sentence>" }],
  "not_scored": ["<dimension id if its surface was absent>"],
  "to_reach_next": [{ "id": "...", "current": 4, "target": 5, "delta": "<against the artifact>", "owner": "<stage/section>", "fix_type": "local", "honesty_note": null }],
  "weighted_avg": 0.0,
  "overall": 0.0,
  "caps_applied": ["<gate id or none>"]
}
```

The "quote a span as evidence" rule keeps scoring repeatable; the `to_reach_next` block is what makes the output improvable instead of merely scored.
