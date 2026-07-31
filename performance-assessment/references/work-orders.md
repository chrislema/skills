# Output formats — the report and the work orders

Two markdown files: `performance-report.md` for humans, `work-orders.md`
for a Sonnet-class executing model. Both are required.

## Why work orders are written this way

The executor is competent but literal, and this audit hands it the most
invasive changes of the three assessments — deletions and structural
rewrites. Every order is **self-contained**, **bounded** (explicit
do-not-touch list), and **verifiable in both currencies**: behavior
provably identical (baseline + characterization tests) and the claimed
improvement provably delivered (the before→after numbers). An order
whose improvement can't be stated as a checkable number or count is not
ready — return it to the report.

## `performance-report.md` structure

1. **Summary** — counts by track and priority; the top 3 in a sentence
   each; total deletable LOC.
2. **Scale assumptions** — the data sizes and traffic shape the audit
   assumed, stated plainly so a reader can reject them.
3. **Baseline harness** — tests found/built, exact commands, green
   list, and the performance baseline table (route → median timing,
   query count, payload size).
4. **Ranked findings** — each: ID (PF-nn), track (A/B), evidence tier
   (MEASURED / CONFIRMED / LIKELY), the evidence itself (numbers or
   file:line + quoted code), for Track B the maintenance-tax statement,
   and the proposed change in one sentence.
5. **Leave-it-alone list** — mandatory. Things examined and deliberately
   not flagged, with one line each on why the simple version is
   correct. This is the section that proves the audit isn't
   complexity-hunting for sport.
6. **Needs-harness-first list** — findings whose blast radius the
   harness can't yet cover, and the test that would unlock each.

## `work-orders.md` structure

Header block:

```markdown
# Work Orders — Performance
Baseline command: <exact command>
Baseline state: <N green, pre-existing failures by name>
Performance baseline: <table or pointer to report §3>
Global rules for the executor:
- Execute in listed order. One order = one commit.
- Run the baseline after EVERY order — all green, characterization
  snapshots byte-identical, or STOP and revert.
- Touch only listed files. Needs another file? STOP and report back.
- Preserve behavior exactly: same status codes, same response shapes,
  same ordering, same error messages. "Improved" output is a failure.
- Do not add caches, indexes, queues, or abstractions beyond what the
  order specifies — even if you spot an opportunity. Note it, skip it.
- For deletions: delete fully (no commenting-out, no _unused renames,
  no "just in case" re-exports). Git is the archive.
```

Then each order:

```markdown
## WO-02 [P1][Track A] Collapse N+1 on GET /api/orders
**Finding:** PF-04 (MEASURED)
**Problem:** `services/orders.js:31` loads orders, then
`views/orders.js:12` fetches each order's customer individually.
Baseline: 41 queries, 620ms median at seed scale (40 orders).
**Change:** In `services/orders.js:31`, include the customer relation in
the initial query (`include: [Customer]` on the existing findAll). Remove
the per-item fetch at `views/orders.js:12-14`; read the included
`order.customer` instead.
**Do not touch:** other order routes, the Customer service, pagination
logic (separate order WO-05).
**Verify (behavior):** full baseline green; characterization snapshot
for GET /api/orders byte-identical.
**Verify (improvement):** re-run the query-count capture from the
baseline recipe — expect 1–2 queries (was 41). Record the number in the
commit message.
**Expected before→after:** 41 queries → ≤2; ~620ms → materially lower
(timing is noisy locally; the query count is the check that matters).
```

Field notes:

- **Priorities**: P0 = user-felt speed win on a hot path, low risk;
  P1 = high-churn maintenance-tax relief or remaining MEASURED speed
  wins; P2 = dead-code deletions (cheap, near-zero risk — front-load a
  few if the user wants visible momentum); P3 = everything else worth
  doing. Cold-path and low-churn items usually don't earn an order at
  all — leave them in the report.
- **Structural (Track B) orders** state the change as an explicit
  operation, not an aspiration: "inline `OrderServiceInterface` into
  `OrderService`, delete the interface file, update these 3 imports
  (listed)". Include the files-to-touch-per-change count before→after as
  the checkable improvement number. If the operation can't be written
  that concretely, it isn't ready for the executor.
- **Deletion orders** enumerate every deleted symbol/file and cite the
  Phase 3 unreachability evidence inline, so the executor (and a
  reviewer) can re-check without the report.
- **One structural change per order.** Never combine a rewrite with a
  deletion, or two layer-collapses, in one order — reverts must stay
  cheap and attribution clean.
- **Sequencing**: deletions that a structural order would touch come
  AFTER that order (don't delete what a rewrite is about to reshape).
  State dependencies explicitly ("requires WO-03 completed").
- **Numbers discipline**: before→after claims come from the baseline
  recipe re-run, measured the same way. Timing claims allow noise
  language; query counts, payload bytes, LOC, and files-to-touch counts
  are exact.
