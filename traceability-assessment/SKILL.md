---
name: traceability-assessment
description: "Full-stack traceability audit for a web application: trace every UI interaction (link, button, form, fetch) down through routing, authentication/authorization, business logic, models, and storage — and back up the response path — to find contract drift between layers: renamed or mismatched parameters (emp_ID vs empID), wrong argument counts or order, type drift, orphaned endpoints, phantom UI calls, fields lost on the return trip. Use when multiple agents (or people) have worked on one codebase and their assumptions may have diverged, when 'the button does nothing', when an API and its callers feel out of sync, or before a release to prove every user-facing action still connects end to end. Builds a characterization-test baseline first, then outputs a trace matrix plus prioritized, Sonnet-executable work orders with per-item verification recipes."
---

# Traceability Assessment — prove every wire is connected

When multiple agents work on a single codebase, each one makes local
assumptions: what a parameter is called, how many arguments a function takes,
what shape the storage layer returns. Each assumption is reasonable alone.
Together they drift. The result is a system where the UI renders, the server
starts, nothing crashes on boot — and a button quietly does nothing because
somewhere between the click and the database, `emp_ID` became `empID`.

This skill audits **the seams**, not the layers. Code inside a layer is
usually consistent with itself; it is the handoffs between layers where drift
accumulates. The unit of work is a **trace**: one UI interaction followed down
through every tier to storage and back up to the rendered result. The audit is
done when every interactive element in the application has a trace, and every
trace has a verdict.

**Prime directive: this skill does not fix anything.** It produces (1) a
baseline test harness proving what works today, (2) a trace matrix, and (3) a
prioritized set of work orders written precisely enough that a Sonnet-class
model can execute them and verify it broke nothing. Read
`references/work-orders.md` before writing the output.

## Phase 0 — Recon

Before tracing anything, map the territory. Identify and record:

- **Stack**: framework(s) per tier, ORM/query layer, storage engines, auth
  mechanism (sessions, JWT, middleware names).
- **The tier list for THIS app.** The canonical tiers are: UI templates/
  components → client-side JS (fetch/XHR/form actions) → route definitions →
  auth/authz middleware → handlers/controllers → services/business logic →
  models/data access → storage schema (migrations, table/collection defs) →
  serialization back up (what the response actually contains) → UI consumption
  of the response. Collapse tiers the app doesn't have; never skip one it does.
- **How to run it**: build command, dev server, test command, seed data. If
  the app cannot be run, say so in the report — several checks degrade to
  static analysis only, and the report must mark which.
- **Entry-point inventory**: enumerate every interactive element. Grep
  templates/components for `href`, `onClick`/`@click`/`hx-*`, `<form`,
  `fetch(`, `axios`, `$.ajax`, route helpers. Also enumerate the reverse
  side: every route the server defines. The two lists bound the audit; count
  both and put the counts in the report so coverage is checkable.

## Phase 1 — Baseline harness (before any findings)

Findings without a safety net are dangerous: the executing model will change
code, and it must be able to prove it changed nothing else. Build the net
first.

1. **Inventory existing tests.** Run them. Record pass/fail exactly. Failing
   tests are baseline facts, not things to fix — record them so the executor
   knows they were already red.
2. **Assess coverage against the entry-point inventory.** For each traced
   interaction that has no test exercising its path, the harness is
   incomplete.
3. **Build characterization tests** for the gaps you can reach: HTTP-level
   tests that hit each route with realistic input and snapshot status code +
   response shape (keys, not volatile values). Characterization tests capture
   behavior *as it is*, including behavior you suspect is wrong — the point is
   detecting change, not asserting correctness. Where a route is broken today,
   write the test to assert the broken behavior and tag it `BROKEN-AS-BASELINE`
   so a fix flips it intentionally.
4. **Record the green list**: the exact command(s) and the exact expected
   results. Every work order will reference this.

Keep the harness cheap: prefer HTTP-level request tests over browser
automation; use browser automation only for interactions that exist purely
client-side. Put harness files in the project's existing test layout.

## Phase 2 — Tier inventories (fan out)

Spawn one sub-agent per tier (or per tier-pair in small apps). Each sub-agent
produces a **contract inventory** for its tier — a structured listing of what
the tier exposes and what it consumes. This is mechanical extraction, not
judgment:

- **Exposes**: every function/route/method other tiers can call — its name,
  parameter names *in order*, parameter types where declared, return shape.
- **Consumes**: every call the tier makes downward — callee name, arguments
  passed *in order*, names used, fields read from the result.
- **Names as written**: never normalize. `emp_ID`, `empID`, and `employeeId`
  are three different strings; recording them faithfully is the whole point.

For the storage tier, the inventory is the schema itself: tables/collections,
column/field names, types, constraints, plus every raw query string found in
code. See `references/seam-checks.md` for the full extraction spec per tier.

## Phase 3 — Seam matching (the actual audit)

Join adjacent tier inventories. For every consume-record in tier N, find its
expose-record in tier N+1 and check the match. The complete checklist is in
`references/seam-checks.md`; the headline checks:

- **Name drift**: caller and callee use different identifiers for the same
  thing (`emp_ID` vs `empID`), including casing-convention breaks and
  JSON-key mismatches between what the client sends and what the server reads.
- **Arity and order**: argument count mismatches, swapped positional args
  (two string parameters in the wrong order type-check fine and fail
  silently).
- **Type drift**: string IDs meeting integer columns, dates as strings vs
  Date objects, nullability assumptions.
- **Query-to-schema match**: every column named in a query exists in the
  schema; every parameter placeholder is bound; ORM field names map to real
  columns.
- **Orphans and phantoms**: endpoints no UI calls (orphans — possibly dead,
  possibly a missing UI wire) and UI calls with no endpoint (phantoms —
  guaranteed 404s).
- **The return trip**: drift on the way *up* is the most-missed class. Check
  that what storage returns survives serialization, that the handler's
  response includes the fields the client destructures, and that the UI
  binds fields that actually exist in the payload.
- **Auth continuity**: every route in a protected area actually passes
  through the auth middleware; authorization checks reference the same
  role/permission names the auth layer issues. (Deep security review is the
  security-assessment skill's job — here you only verify the *wiring* is
  continuous.)

Every UI entry point gets a row in the **trace matrix** with a verdict:
**CLEAN** (full path verified), **DRIFT** (connected but with a mismatch that
works by luck or partially), **BROKEN** (the path dies at an identified
layer), or **UNTRACEABLE** (dynamic dispatch/reflection prevented static
tracing — flag for runtime verification).

## Phase 4 — Adversarial verification

Before a finding enters the report, try to kill it. A false positive here
costs double: the executing model will "fix" working code. For each candidate
finding, a verifier (fresh sub-agent when the count is high) must:

1. Re-read the actual code at the cited locations — not the inventory
   summary.
2. Check for aliasing/mapping layers that reconcile the mismatch (serializers,
   DTO mappers, ORM column aliases, destructuring renames).
3. Where the app runs, reproduce it: click the path or curl the route and
   observe the failure.
4. Assign confidence: **CONFIRMED** (reproduced or mismatch is unambiguous in
   code) or **LIKELY** (static evidence only). Report both; work orders are
   only written for CONFIRMED unless the user asks otherwise.

## Phase 5 — Output

Produce two artifacts, per the formats in `references/work-orders.md`:

1. **`traceability-report.md`** — the trace matrix (every entry point, every
   verdict), coverage counts vs the Phase 0 inventory, the baseline harness
   description and green list, and the findings with evidence.
2. **`work-orders.md`** — prioritized, self-contained work orders for a
   Sonnet-class executor. Priority order for this skill: BROKEN paths on
   primary user flows first, then BROKEN on secondary flows, then DRIFT that
   loses data, then DRIFT that is currently harmless, then orphans/phantoms
   (cleanup). Every work order carries its own verification recipe against
   the Phase 1 baseline.

Do not editorialize about architecture in the work orders. The executor's
job is to reconnect wires, not remodel the house.
