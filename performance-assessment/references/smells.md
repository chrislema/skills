# Smell catalog — both hunts, with false-positive traps

Backs Phase 2. Track A is speed and waste; Track B is complexity and
speculation. Every entry: what it looks like, why it costs, and the trap
— the legitimate version of the same pattern that must NOT be flagged.
The trap column is what separates this audit from a lint run.

## Track A — speed and waste

### Storage
- **N+1 queries** — a query inside a loop over a prior query's results;
  ORM lazy-loading relations accessed per-item in a view. *Cost*: linear
  query count with data size. *Trap*: the loop is bounded and small by
  construction (iterating 3 config rows), or the ORM batches under the
  hood (dataloader) — check the actual emitted queries, not the code
  shape.
- **Missing index** — a WHERE/ORDER BY/JOIN predicate on an unindexed
  column, on a table that is or will plausibly grow past ~10k rows.
  *Trap*: tiny tables; write-heavy tables where the index costs more
  than it saves; the index already exists via a composite whose prefix
  covers it.
- **Unbounded queries** — user-facing lists with no LIMIT/pagination;
  `findAll()` feeding a UI. *Trap*: admin/export endpoints where full
  results are the point (still note payload/timeout risk, lower
  priority).
- **SELECT-star over-fetch** — wide rows fetched to read two fields, at
  scale or over the network. *Trap*: at small scale this is idiomatic
  and clearer — only flag with row width × volume worth caring about.
- **Queries in transactions holding I/O** — transaction spans an
  external call (HTTP, email), holding locks. *Trap*: intentional
  outbox-pattern writes.

### Server
- **Sync I/O in request path** — blocking file/network/crypto calls in a
  handler on a concurrent server; `JSON.parse` of huge payloads inline.
  *Trap*: startup-time code, CLI scripts, workers where blocking is the
  model.
- **Sequential awaits, independent work** — `await a(); await b();`
  where a and b don't depend on each other and both hit I/O. *Trap*:
  dependency is real but non-obvious (b relies on a's side effect);
  deliberate rate-limit ordering.
- **Recomputed invariants** — per-request recomputation of things that
  never change per deployment (parsing config, compiling regexes/
  templates, building lookup maps). *Trap*: hot-reload semantics in dev
  that prod shares deliberately.
- **Missing pagination on growth surfaces** — endpoints fine today whose
  backing collection only grows (logs, orders, messages). This is the
  ONE forward-looking claim Track A may make, because growth is
  observed, not speculative.

### Payload & client
- **Over-fetching APIs** — endpoints returning far more than any caller
  reads (cross-check callers; the traceability inventory helps).
  *Trap*: published/external API where extra fields are contract.
- **Unpaginated list rendering** — the UI renders everything it gets;
  pairs with unbounded queries into a compound finding.
- **Dead weight in bundles** — dependencies imported for one function
  with a stdlib equivalent, moment-style libraries where Intl suffices.
  *Trap*: tree-shaking may already drop it — check build output if
  available, else mark INFERRED.

### Dead code (everywhere)
- Unreachable branches (conditions provably constant), uncalled
  unexported functions, routes with no callers, unused dependencies,
  fully-rolled-out feature flags, commented-out blocks, `utils` graveyard
  functions. *Trap*: dynamic dispatch/reflection/template references;
  external callers (public API, cron, webhooks); test-only helpers that
  look uncalled from src. Deletion candidates need the Phase 3
  unreachability proof, not just zero grep hits in the audited slice.

## Track B — complexity and speculation

- **Single-implementation interface** — interface/abstract base with one
  concrete class, no second on any roadmap. *Cost*: every reader
  traverses the indirection; every change touches two files. *Trap*: the
  interface is a genuine test seam actually used by tests/mocks; the
  framework requires it (DI containers); a second implementation exists
  outside the audited slice.
- **Pass-through layers** — service methods that one-to-one forward to a
  model/repository call; controllers that only call one service method
  and return it. *Cost*: files-to-touch-per-change multiplies. *Trap*:
  the layer is thin *now* but siblings in the same layer do real work —
  uniformity has value; flag only when the whole layer is hollow.
- **Caching without receipts** — a cache nobody measured: memoized cheap
  calls, cached queries that change per-request, TTL logic more complex
  than the computation. *Cost*: staleness bugs and invalidation code
  forever. *Trap*: the cache IS load-bearing but the measurement lives
  elsewhere (an incident, a comment, git history) — check before
  flagging.
- **Config for a day that never comes** — settings never set to a second
  value, plugin registries with one static entry, "strategy" selection
  that always selects the same strategy, env switches nothing switches.
  *Cost*: readers must consider possibilities that never occur. *Trap*:
  genuinely deployment-varying config (per-env values in infra you can't
  see) — check deploy configs before flagging.
- **Premature DRY** — one shared helper serving two callers via mode
  flags and optional params; "reuse" that made both call sites harder to
  read than two plain functions. *Cost*: changes for caller A risk
  caller B. *Trap*: three-plus callers with true shared logic — that's
  earned DRY; don't unshare it.
- **Speculative generality** — visitor/registry/event patterns over a
  small fixed set of cases; generic type parameters instantiated once;
  message indirection between two components that could just call each
  other. *Cost*: the pattern's cognitive tax, paid by every reader,
  yielding nothing. *Trap*: the fixed set is genuinely about to grow
  (check roadmap/issues/user statements before flagging).
- **Boolean-flag functions** — `doThing(data, true, false)` — flags that
  split a function into disjoint behaviors sharing a name. *Cost*:
  every call site is a puzzle. *Trap*: a single flag with obvious
  meaning at a single call site is fine; flag when flags multiply or
  callers hardcode different combinations.
- **Scattered state machines** — lifecycle expressed as independent
  booleans (`isLoading`, `isDone`, `hasError`) with implicitly invalid
  combinations. *Cost*: impossible states ship. This is a
  simplification finding when the states are enumerable.
- **Wrapper worship** — in-house wrappers around stable libraries adding
  renamed methods and nothing else. *Trap*: the wrapper pins a
  swap-prone dependency or adapts a genuinely unstable API; wrappers
  with added behavior (retries, logging) are earning their keep.
- **Complexity hotspots** — long deeply-nested functions, files
  everything imports, giant conditional ladders that are a lookup table
  wearing a trenchcoat. Flag with the specific simplification, not
  "refactor this".

## Priority guidance

Rank by felt cost over risk: user-visible latency on hot paths (MEASURED)
first; maintenance tax on frequently-edited code (check git churn — high
churn × high complexity is the jackpot quadrant) second; dead-code
deletion third (near-zero risk, real reading-cost relief); cold-path
inefficiencies and low-churn complexity last — often correctly left
alone. The report's "leave it alone" section is mandatory: it records
what was examined and deliberately not flagged, so the audit's silence is
information rather than omission.
