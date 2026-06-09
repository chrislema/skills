# Red Dot — canonical spec schema

The eight stages contribute to one `spec.json`. Keys, and the stage that owns each:

| key | owner stage | purpose |
|---|---|---|
| `positioning` | 0 | customer, offer, transitions worth money, voice |
| `banned_phrases` | 0 | voice-gate lint list |
| `cases` | 1 | design-time case bank (not shipped to runtime) |
| `lifecycle_model` | 2 | stages, each with both faces + a say-it-out-loud name |
| `stuck_map` | 2 (4 fills `detected_by`) | transition failures by boundary, typed by locus |
| `gap` | 3 | chosen gap family + benchmark source |
| `axes` | 3 | measured axes and their item counts |
| `scoring` | 3 (5 finalizes) | address-schema params (thresholds, band cuts) |
| `questions` | 4 | 10–15 items, axis/theme-tagged, options in rung order |
| `exemplars` | 5 | known cases for the exemplar test |
| `content` | 6 | atom bank (openers/body per address) + depthLeads, with variant banks |
| `offer` | (1+, optional) | activates the commercial-closure gate |
| `maturity_stages` | (2, optional) | activates the two-faced gate |
| `ranking` | (optional) | activates ranking-gap-derived + positional gates |
| `design_notes` | (optional) | editorial copy for the design document (`thesis`, `benchmark_note`, `woven_not_scored`, `corrections`) |

## Optional fields the design document reads

`scripts/design_doc.py` (Stage 7's second emit) derives the whole framework
walkthrough from the spec, and renders these OPTIONAL annotations when present —
all ignored by the engine and the gates:

- `questions[].reads` — short label of what the item measures (becomes the item heading).
- `questions[].catches` — the failure mode it detects (a one-liner under the heading).
- `axes.<axis>.label` — used to title any non-self/team group (e.g. a `journey`/commitment axis).
- `design_notes` — the §0 thesis, the benchmark-axis intro, the "woven not scored" list, and extra "yours to correct" items.

## Runtime-relevant subset (what the engine reads)

`meta`, `questions`, `scoring`, `content`, `banned_phrases`, and when present
`stuck_points`, `offer`, `maturity_stages`, `ranking`.

## Reference scoring shape (two-strand quadrant)

```
"axes":    {"self": {"items": 7}, "team": {"items": 5}}
"scoring": {"quadrant": {"threshold": 3.0},
            "bands": {"aligned": {"measure":"mean","cut":4.0,"high":"compounding","low":"solid"},
                      "lone":    {"measure":"gap","cut":1.3,"high":"wide","low":"opening"}, ...}}
"content": {"quadrants": {"lone": {"name":"...","gap_family":"correlational",
                          "validate_first":false,"opener":["v1","v2"],"body":["...","..."]}, ...},
            "depthLeads": {"lone|opening":"...", "lone|wide":"...", ...}}
```

For a richer address schema (e.g. stage × locus × theme × gap-state), generalize
the resolver in `engine.py` (`reachable`, `compile_landings`) and
`gate_check.py` (`reachable_addresses`) accordingly; the gate logic is unchanged.


Back to the [router](../SKILL.md).
