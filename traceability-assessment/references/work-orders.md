# Output formats — the report and the work orders

The audit produces two markdown files in the project root (or where the
user directs): `traceability-report.md` for humans, `work-orders.md` for a
Sonnet-class executing model. Write both; they serve different readers and
neither substitutes for the other.

## Why work orders are written this way

The executor is a competent but literal model. It will do exactly what the
order says, it will not infer unstated intent, and it must be able to prove
it broke nothing. Therefore every order is **self-contained** (readable
without the report), **bounded** (says what NOT to touch), and
**verifiable** (carries its own test recipe). If you cannot write the
verification recipe for a finding, the finding is not ready to be a work
order — downgrade it to a report-only observation.

## `traceability-report.md` structure

1. **Summary** — counts: entry points found, traces run, CLEAN / DRIFT /
   BROKEN / UNTRACEABLE, findings by confidence.
2. **How to read this** — one paragraph for a reader who wasn't present.
3. **Baseline harness** — what existed, what was built, the exact command
   to run it, the recorded green list (and pre-existing red list).
4. **Trace matrix** — full table, every entry point.
5. **Findings** — each with ID (F-nn), confidence (CONFIRMED/LIKELY),
   evidence (file:line for BOTH sides of the seam), and reproduction
   (what you clicked/curled and what happened), in plain prose.
6. **Untraceable inventory** — what static analysis couldn't follow and
   what runtime check would settle it.

## `work-orders.md` structure

Header block first:

```markdown
# Work Orders — Traceability
Baseline command: <exact command>
Baseline state: <N passing, M pre-existing failures listed by name>
Global rules for the executor:
- Complete orders in listed sequence. One order = one commit.
- Run the baseline command after EVERY order. Any new failure not named
  in the order's "expected test changes" means STOP and revert the order.
- Touch only the files listed in the order. If the fix seems to require
  touching another file, STOP and report back instead of improvising.
- Never "improve" adjacent code, rename for consistency beyond the order's
  scope, or fix things you notice along the way. Note them; don't do them.
```

Then each order:

```markdown
## WO-03 [P1] Reconnect "Save Employee" — body key mismatch
**Finding:** F-07 (CONFIRMED)
**Problem:** `js/staff.js:142` sends `{ emp_ID, name }`;
`controllers/employee.js:58` reads `req.body.empID`. The update silently
writes `undefined` as the id and the save no-ops.
**Canonical form:** `empID` — it is what the model layer and schema use
(`models/employee.js:12`, migration `004_employees.sql`). Change the
CLIENT to match, not the server.
**Change:** In `js/staff.js:142` (only), rename the body key `emp_ID` →
`empID`.
**Do not touch:** `controllers/employee.js`, other `emp_ID` occurrences
(they belong to WO-04), anything else.
**Verify:**
1. `npm test` — all baseline-green tests still green.
2. `npm test -- --grep "employee update"` — the characterization test
   `PUT /api/employees/:id BROKEN-AS-BASELINE` now FAILS its old broken
   snapshot; update that one test to assert the working behavior (200 +
   persisted name change) and confirm it passes.
3. No other test output changes.
**Expected test changes:** exactly the one test named above.
```

Field notes:

- **Priority**: P0 = BROKEN on a primary user flow; P1 = BROKEN on
  secondary flow; P2 = DRIFT that loses or corrupts data; P3 = DRIFT
  currently harmless; P4 = orphan/phantom cleanup. Within a priority,
  order so that no order depends on a later one.
- **Canonical form** is mandatory for every naming/contract fix: the
  executor must never guess which side of a mismatch is "right". State
  the rule you used (the layer closest to storage usually wins; a
  published/external API contract always wins) and cite where the
  canonical name lives.
- **Do not touch** is not boilerplate — enumerate the specific tempting
  files. Drift fixes are where an eager model creates new drift by
  "consistency" renaming across the codebase.
- **Grouped orders**: if one mismatch appears at many sites, one order may
  list all sites explicitly. Never write "and anywhere else it appears" —
  the executor must not grep-and-replace beyond the enumerated list.
- **BROKEN-AS-BASELINE flips**: when a fix intentionally changes behavior
  a characterization test froze, the order must name that test and state
  the new expected assertion. That is the only situation where the
  executor edits a test.
