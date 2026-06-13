# Cloudflare primitive selection — reference

Read this when doing Pass 4 (runtime architecture sketch). It encodes the
selection logic for mapping classified capabilities onto Cloudflare first-class
citizens.

## Storage selection

| If the Resource File / state is… | Use | Why |
|---|---|---|
| Small (<25MB), read-hot, write-rare (rubrics, taxonomies, prompt scaffolds, config) | **KV** | Edge-cached reads, eventual consistency is fine for versioned design-time artifacts |
| Relational, queryable, per-tenant, or transactional (sessions, results, tenants, queues, audit logs) | **D1** | SQL, joins, per-row writes; pair with indexes on tenant + created_at from day one |
| Large blobs or many files (compiled HTML artifacts, exemplar corpora, exports, PDFs) | **R2** | Cheap at volume, no egress fees, presigned URLs for delivery |
| Per-entity stateful coordination (a live assessment session, a rate limiter, a build lock) | **Durable Objects** | Single-threaded consistency per entity; only reach for this when KV/D1 races actually hurt |
| Scheduled or queued work (nightly Resource File recompiles, batch S-class runs) | **Queues + Cron Triggers** | Decouples slow AI calls from request path |

## Workers AI (S-class) invocation pattern

Every Scout-class call follows the same wrapper, no exceptions:

1. **Assemble**: load the specific Resource File(s) from KV; interpolate into a
   fixed prompt template (the template itself is a versioned Resource File).
2. **Constrain**: demand JSON against a schema stated in the prompt; keep the
   output space enumerated (labels, ids, selections — not free prose where
   avoidable).
3. **Validate (D-class)**: parse, schema-check, and *semantically* check (is
   the returned label in the allowed set? is the selected atom id real?).
4. **Retry once** with the validator's error appended.
5. **Degrade deterministically**: on second failure, take the authored default
   path (default landing, generic variant, queue for review). Log the failure
   with the Resource File version. A user must never see a stuck or raw-error
   state because a 17B model had a bad day.

Prompt-size discipline: Scout-class quality degrades as context grows. Budget
the prompt — one task, one Resource File slice, a handful of exemplars. If the
prompt wants three Resource Files, the task is probably two tasks.

## The editorial-pass pattern (the usual shape of surviving F)

When F survives the demotion moves, it is almost always review, not authoring:
one metered call per run over a compiled, human-readable rendering of the
draft (a design doc, not raw JSON), returning a structured verdict against a
**versioned rubric** (the rubric is itself a Resource File): approve / patch
(returns concrete edits, applied deterministically) / regenerate-with-notes
(loops the relevant S step once). Hard per-tenant budget in D1; on cap or
outage the run completes with the verdict marked SKIPPED — the deterministic
gates own the floor, the editorial pass only buys ceiling. Quarterly, audit a
sample of *approved* runs, not just rejections: an editor's blind spots
become the product's reputation, and editorial checks that fire identically
are lints waiting to be written.

## F-class (frontier runtime) pattern

When an F-class capability survives the redesign attempt:

- Route via a Worker to the Claude API; never from the client.
- Cache aggressively (KV keyed on a hash of inputs + Resource File version) —
  much "runtime" frontier work is the same question asked repeatedly.
- Hard budget caps per tenant per day, enforced in D1, with the deterministic
  degradation path taking over at the cap.
- Treat every F-class call site as a standing invitation to do more design-time
  work: log the inputs/outputs, and periodically run a Claude design session
  over the logs to grow the Resource File until the call site demotes to S or R.
  **F-class is a queue, not a destination.**

## The demotion ratchet (the long game)

The architecture should make intelligence flow downhill over time:

```
F (frontier runtime) → S (scaffolded cheap runtime) → R (Resource File) → D (code)
```

Every class boundary gets a logging hook so the design-time sessions have the
raw material to push capabilities down a level. A healthy product's F and S
share shrinks release over release; its Resource Files and code grow. That is
the operational meaning of "design-time AI vs runtime AI."
