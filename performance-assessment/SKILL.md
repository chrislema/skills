---
name: performance-assessment
description: "Performance and complexity audit of a web application that hunts in both directions: classic performance debt (N+1 queries, missing indexes, unbounded result sets, sync I/O in hot paths, oversized payloads, dead code) AND over-engineering — premature optimization, speculative abstraction, caching layers that cache nothing, configuration for a day that never comes, indirection with a single implementation. The goal is a system that performs the same functions cleaner, faster, and with less maintenance risk — deleting code counts as a win. Use for a performance review, 'why is this slow', a complexity/simplification pass, dead-code cleanup, 'this codebase feels over-built', or after AI agents have layered abstractions onto a codebase. Builds a characterization-test baseline first so behavior is provably preserved, then outputs prioritized, Sonnet-executable work orders where every claim is backed by evidence — measured cost or demonstrated maintenance risk, never vibes."
---

# Performance Assessment — same functions, cleaner, faster, less to maintain

Performance debt comes in two opposite shapes, and most audits only hunt
one. The first is the classic kind: the N+1 query, the missing index, the
endpoint that loads the whole table to show ten rows. The second is
subtler and often costs more over a system's life: code that is *right*
but too complex — the abstraction built for a second implementation that
never came, the caching layer that saves nothing measurable, the
config system with one config. Premature optimization and speculative
generality are performance problems too: they slow down every future
change, and future changes are where systems spend most of their lives.

This skill hunts both. Its output is a set of changes that keep the
system's observable behavior identical while making it cleaner, faster,
and cheaper to maintain. **Deleting code is a first-class win** — often
the biggest one available.

**Prime directive: every finding carries evidence, and the evidence names
its currency.** A speed finding cites a measurement or a mechanically
demonstrable cost (a query count, a payload size, an O(n²) loop over an
unbounded collection). A complexity finding cites demonstrated
speculation (one implementation behind an interface, a flag never set, a
cache with no measurable hit value) and states what maintenance it taxes.
"This could be faster" and "this looks over-built" are not findings.
The full catalog of what to hunt — and the false-positive traps for each —
is in `references/smells.md`.

**Second directive: do not become the disease.** The audit must not
propose its own premature optimizations. Never recommend adding a cache,
a queue, an index, or an abstraction without evidence of present, felt
cost — the same standard the audit holds the codebase to. When current
code is simple and fast enough, "leave it alone" is the correct verdict,
and the report should say so where it applies. Simplicity today beats
throughput the app will never need.

## Phase 0 — Recon

- **Stack and hot paths**: framework, storage, ORM; then identify the
  routes/jobs that matter — the primary user flows, anything in a loop or
  cron, anything the user says is slow. Effort follows heat: an O(n²) in
  a startup script run once a day is a note, not a P1.
- **Run state**: can the app run with realistic-ish data? Real measurement
  beats static inference everywhere it's available. Check for existing
  query logging / profiling hooks. If the app can't run, mark findings
  INFERRED vs MEASURED throughout.
- **Scale reality**: find the actual data scale (row counts if reachable,
  seed sizes, pagination defaults). "Missing index" on a 200-row table is
  not a finding. Record the scale assumptions the audit is making —
  they're part of the report.

## Phase 1 — Baseline harness

Simplification is behavior-preserving surgery, and this audit proposes the
most invasive changes of the three assessments — deletions and structural
rewrites. The harness carries the whole burden of proof.

1. Inventory and run existing tests; record exact pass/fail baseline.
2. Build **characterization tests around every region a finding will
   touch**: HTTP-level tests snapshotting status + response shape +
   ordering for the affected routes, with enough input variety to pin the
   behavior (empty results, pagination edges, error paths). For a
   candidate deletion, the characterization tests prove the *surviving*
   behavior; for a rewrite, they fence the rewritten function.
3. Capture a **performance baseline** where the app runs: timing per
   audited route (median of repeated local runs — crude is fine, note the
   noise), query counts per route (from ORM/query logs — the N+1
   signature), payload sizes. These numbers are the before-photo the
   work orders' claims are checked against.
4. Record commands and the green list.

A finding whose blast radius the harness cannot cover does not become a
work order. It stays in the report marked "needs harness first", with a
note on what test would unlock it.

## Phase 2 — The two hunts (fan out)

Spawn sub-agents along two tracks, working from `references/smells.md`:

**Track A — speed and waste** (per layer):
- Storage: N+1 patterns, missing indexes on actual query predicates,
  `SELECT *` feeding narrow needs, unbounded queries (no LIMIT on
  user-facing lists), queries in loops, transactions held across I/O.
- Server: sync/blocking I/O in request paths, sequential awaits that
  could be parallel, per-request work that could be computed once,
  chatty service-to-service calls, missing pagination.
- Payload/client: over-fetching APIs, unpaginated list endpoints,
  render-blocking loads of things not needed, bundles shipping unused
  weight.
- Everywhere: dead code — unreachable branches, unexported-and-uncalled
  functions, routes nothing calls (cross-check the traceability audit's
  orphan list if one exists), dependencies imported nowhere, feature
  flags fully rolled out or permanently off.

**Track B — complexity and speculation** (whole-codebase eye):
- Interfaces/base classes with exactly one implementation and no second
  one in sight.
- Layers that only forward: services that wrap a model call one-to-one,
  handlers that only call one service method, wrappers around libraries
  adding nothing.
- Caching without receipts: caches whose hit rate nobody measured,
  memoization of cheap or rarely-repeated calls, cache invalidation
  complexity exceeding the cost of just computing the thing.
- Config for a day that never comes: settings with one value ever used,
  plugin systems with one plugin, "extensible" registries with static
  contents, env-var switches nothing switches.
- Generality nobody asked for: generic solutions to specific problems
  (the visitor pattern over three fixed cases), premature DRY (a shared
  helper contorted with flags to serve two callers that should just be
  two functions), event/message indirection between two components that
  could call each other.
- Complexity hotspots: functions past ~50 lines with deep nesting,
  boolean-flag parameters that split a function into two behaviors,
  state machines implemented as scattered booleans.

Track B findings must include the **maintenance-tax statement**: what
concretely gets harder because this exists (e.g. "adding a field
currently requires edits in 4 files across 3 abstraction layers; after
the change, 1").

## Phase 3 — Adversarial verification

Both tracks generate seductive false positives. For each candidate, a
verifier must:

1. **Speed findings**: reproduce the cost where the app runs (trigger the
   route, count the queries, time it). Check the scale reality — is the
   collection actually unbounded? Is this path actually hot? An INFERRED
   finding that can't be measured must survive a re-read for mitigating
   structure (a cache above it, a LIMIT upstream).
2. **Complexity findings**: hunt for the reason the complexity exists.
   Search git history (was the second implementation removed rather than
   never built?), comments, docs, and framework conventions (some
   "pointless" layers are the framework's testing seam). Check who else
   imports/depends on the thing — blast radius beyond the audited area
   kills the finding or escalates it to report-only.
3. **Deletion candidates**: prove unreachability, not just un-calledness
   in the audited slice — dynamic dispatch, reflection, template
   references, external callers (published API, cron, webhooks).
4. Mark MEASURED, CONFIRMED (unambiguous in code), or LIKELY. Work orders
   come only from MEASURED and CONFIRMED.

## Phase 4 — Output

Per formats in `references/work-orders.md`:

1. **`performance-report.md`** — scale assumptions, harness description,
   baseline numbers table, ranked findings with evidence currency
   (MEASURED numbers or CONFIRMED code citations), the "leave it alone"
   list (things examined and rightly left simple — this section keeps
   the audit honest), and "needs harness first" items.
2. **`work-orders.md`** — prioritized for a Sonnet-class executor.
   Ranking: user-felt speed wins at low risk first, then maintenance-tax
   reductions ordered by tax-relieved vs blast radius, then dead-code
   deletions (cheap, satisfying, near-zero risk — good early wins if the
   user wants momentum), then everything else. Every order states the
   expected before→after (query count, timing, LOC removed, files-to-
   touch-for-a-change count) and its verification recipe. Behavior must
   be provably identical: full baseline green, characterization
   snapshots unchanged.
