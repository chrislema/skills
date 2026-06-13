---
name: design-time-audit
description: "Audit any Claude skill, prompt, or project to decompose it for cloud productization — separating design-time AI (frontier-model judgment done once, with Claude) from runtime AI (cheap-model execution on Workers AI / Llama Scout) from deterministic code, and specifying the Resource Files that let a dumber runtime model perform like a smarter one. Use whenever someone wants to productize a skill or workflow, move something from Claude to Cloudflare (Workers, KV, D1, R2, Workers AI), ask 'what here actually needs AI', design a Resource File, plan a runtime architecture for an existing Claude-based process, or estimate what a cheap LLM can and can't carry. Produces two markdown deliverables: an Audit Report and a Forward Strategy."
---

# DesignTimeAudit — decompose a skill for productization

The thesis this skill operationalizes: **intelligence applied once, at design
time, by a frontier model is an asset; intelligence demanded repeatedly, at
runtime, from any model is a cost and a risk.** Productizing a Claude skill is
therefore not "run the skill in the cloud" — it is a decomposition problem.
Every capability in the skill gets sorted into one of five classes (the
taxonomy below), the design-time classes get compiled into **Resource Files**,
and only a small, scaffolded residue is left for a runtime model to perform.

The audit's prime directive: **be suspicious of every claim that AI is needed.**
The order of preference is always: deterministic code first, pre-computed
intelligence second, scaffolded cheap-model AI third, frontier runtime AI last
and only under protest. Most "AI features" in a well-decomposed product turn
out to be a lookup against intelligence that was authored once.

## The five-class taxonomy

Classify every capability, step, judgment, and artifact in the audited skill
into exactly one of these. The classes are ordered: when in doubt, push the
capability **down** the list (toward determinism), never up.

| # | Class | Definition | Cloud home |
|---|---|---|---|
| **D** | Deterministic code | Any step whose output is a function of its inputs: scoring, validation, compilation, routing, templating, state machines, gating. | Workers (TS/JS), D1 for relational state, KV for config, R2 for blobs |
| **R** | Resource File (pre-computed intelligence) | Judgment that is *stable across users/sessions* and can be authored once: taxonomies, decision tables, rubrics, authored content atoms, exemplar banks, classification criteria, prompt scaffolds. | KV (small, hot), R2 (large), D1 (queryable) — versioned, with Claude as the authoring tool |
| **S** | Scaffolded runtime AI (Scout-class) | Judgment that is *instance-specific* but **narrow**: classify this input against a provided rubric, extract these fields, select from this menu, rephrase within these rails. A dumber model performs it acceptably *only because* a Resource File carries the intelligence. | Workers AI (e.g. Llama 4 Scout) + Resource File in the prompt, output constrained to JSON, validated by D-class code |
| **F** | Frontier runtime AI | Instance-specific judgment that is **open-ended** AND survives all four standard demotion moves (Pass 2). Its honest signature: asymmetric, ungradeable errors. Typically ends up as one bounded editorial pass, not an authoring role. | Claude API via Worker, with caching, budget caps, and a deterministic fallback |
| **H** | Human-in-the-loop | Steps whose value *is* the human: expert correction, taste approval, accountability sign-off. Never simulate these with AI — the audit flags any temptation to. | UI surfaces, async review queues (D1 + email/Slack via Workers) |

Two structural observations that recur in almost every audit — look for them:

1. **Design-time AI is usually the skill itself.** A well-built Claude skill is
   already mostly class-R intelligence wearing class-F clothing: its method
   docs, taxonomies, and templates are Resource Files that happen to currently
   require Claude to interpret them. The audit's job is to find where the
   interpretation can be compiled out.
2. **The S/F boundary is the money line.** Everything hinges on whether the
   runtime judgment can be narrowed enough for a Scout-class model. The lever
   is always the same: move generality into the Resource File (more cases,
   tighter rubric, enumerated outputs) until the runtime task is recognition,
   not generation. If you cannot enumerate the output space, you have not
   finished designing.
3. **Difficulty is not the test; gradeability is.** The classic
   misclassification is marking a capability F because doing it *well in one
   pass* is hard. Wrong test. If the audited skill already ships a grader —
   lints, gates, validators, rubrics — then "hard in one pass" decomposes into
   **draft (S) → lint (D) → review (F-as-editor)**, and the frontier share
   collapses to the editing margin. Always ask: does the eval already exist?
   A bundled checker script is the author confessing the capability is
   gradeable, and gradeable means demotable.

## The audit procedure

Run these six passes in order. Passes 1–4 produce the Audit Report; passes
5–6 produce the Forward Strategy. Both deliverables are **markdown files**.

### Pass 1 — Inventory
Read the *entire* skill graph: SKILL.md, every stage/reference/concept file,
every bundled script and asset. Build a flat inventory of capabilities — each
discrete thing the skill does or decides. A "capability" is a unit small
enough to classify cleanly: "elicit cases by interview" and "tag each case
symptom/cause/misdiagnosis" are two capabilities, not one. Note for each:
where it lives, what it consumes, what it produces. Bundled scripts are
evidence — anything already in Python/JS is the author telling you it is
class-D.

**Demand usage evidence, and weight it above the docs.** Ask the owner for
real inputs and transcripts from actual runs (briefs, prompts, the artifacts
produced). How a skill is *documented* to work and how it is *demonstrated*
to work routinely diverge, and every divergence is classification gold:
- A documented human loop that real runs skip → that H/F machinery is
  **dormant**, not required; take it off the productized critical path.
- A "design choice" that every real run resolves the same way (reusing a
  bundled reference pattern, picking the same schema) → the choice was made
  once at skill-design time; it is class-R, not class-F, no matter how
  consequential the docs say it is.
- Real inputs shaped differently than the method assumes (free text instead
  of structured cases, patterns instead of stories) → the Resource Files
  must be specified for the inputs that actually arrive.
Classify the skill that runs, not the skill that's written.

### Pass 2 — Classification
Assign every capability a class (D/R/S/F/H) and a **confidence** (high/med/
low). For each, record the one-line justification. Apply the demotion test in
order:
- Can a function compute it? → **D**
- Is the judgment stable across instances (would the answer be the same next
  month, for the next user)? → **R**, and name the Resource File it belongs in.
- Is it instance-specific but performable as *recognition against a provided
  rubric with an enumerable output space*? → **S**, and name the Resource File
  that makes it so.
- Is it instance-specific, open-ended, and irreducible after a serious attempt
  to redesign? → **F**, and say why the redesign failed.
- Is the human the point? → **H**.

A useful forcing question for the S/F line: *"Could I write the eval?"* If you
can write a deterministic grader for the output, a Scout-class model with a
Resource File can usually produce it. If grading itself needs judgment, it's F.
And check whether the eval *already exists* before deciding it can't be
written — bundled gates and lints are pre-built graders.

Before any capability keeps an F, run it through the **standard demotion
moves**. An F classification is only honest after all four fail:

1. **Draft–lint–edit.** Hard-in-one-pass ≠ frontier. Scout drafts against a
   fat Resource File, existing/new D-class lints reject the worst, a bounded
   frontier *editorial pass* reviews the residue. Frontier demotes from
   author to editor — which is most of the cost.
2. **Generation-then-selection.** The standard move for anything that smells
   like "taste" (naming, phrasing, framing). A Resource File encodes the
   grammar of good output plus anti-patterns; Scout generates N candidates; a
   rubric scorer auto-selects (or a human picks post-hoc). A 20% hit-rate
   drafter is a 90%+ workflow when something else is the recognizer.
3. **Archetype instantiation.** The standard move for anything that smells
   like "synthesis" or "induction." Most synthesis in a mature domain is
   recognition of a recurring shape: build a Resource File of archetypes from
   completed builds, and the task becomes classify-then-instantiate.
4. **Decision-table extraction.** The standard move for anything that smells
   like "consequential judgment." If the skill's prose states selection rules
   ("if the cell is X, use Y; never Z"), it has already confessed the
   judgment is a table. Encode it; only genuine ambiguity escalates.

What legitimately survives as F has a recognizable signature: **asymmetric,
ungradeable errors** — failures that pass every deterministic check and cost
heavily downstream (a mis-jointed model that corrupts everything built on it;
flatness that lints can't see). Concentrate the surviving F budget into the
fewest, most bounded review points aimed at exactly those surfaces — typically
one editorial pass per run, with a structured verdict, a hard budget, and a
gated deterministic floor underneath so its absence degrades ceiling, never
correctness.

### Pass 3 — Resource File specification
For every R and S capability, specify the Resource Files. A Resource File spec
names: **purpose** (what runtime question it answers), **shape** (schema or
document structure), **source** (which design-time session/skill stage authors
it), **freshness** (static / per-tenant / per-version), **storage** (KV/R2/D1
and why), and **consumer** (D-class code, S-class prompt, or both). Resource
Files are *products of a Claude design-time session* — say explicitly what
that authoring session looks like, because that session is the new "skill".

Resource File craft rules:
- One file per question, not one mega-file: a runtime prompt should load only
  the intelligence it needs (KV reads are cheap; context windows are not —
  Scout-class models degrade fast as the prompt grows).
- Enumerate, don't describe. "Classify into one of these 7 labels, defined and
  exemplified" beats "use your judgment about the category."
- Embed the exemplars. Few-shot examples in the Resource File are the single
  highest-leverage transfer of design-time intelligence to a dumb model.
- Version every file and stamp the version into runtime outputs, so a bad
  Resource File release is diagnosable and rollbackable like code.

### Pass 4 — Runtime architecture sketch
Map the classified capabilities onto Cloudflare first-class citizens: which
Workers exist, what lives in KV vs D1 vs R2, where Workers AI is invoked and
with what guardrails (JSON-constrained output, D-class validation after every
S-class call, retry-then-fallback). Include the **failure posture**: what
happens when the S-class model returns garbage — there must always be a
deterministic degradation path (a default landing, a generic variant, a queued
human review), never a stuck user.

### Pass 5 — Gap and risk register
What did the decomposition lose relative to Claude-in-the-loop? Be honest:
quality ceilings on S-class composition, the absence of taste, edge cases the
Resource File doesn't cover. For each gap: severity, who notices, and the
mitigation (expand the Resource File / add an F-class escape hatch / accept).

### Pass 6 — Sequencing
Order the build. The default sequence is: **D-spine first** (the deterministic
skeleton end-to-end, with Resource Files stubbed), **R second** (author the
Resource Files in Claude design sessions), **S third** (wire Workers AI into
the now-proven spine), **F/H last** (escape hatches and review surfaces). Ship
the thinnest path that exercises every storage and compute primitive before
authoring content at volume.

## Deliverable 1 — the Audit Report

ALWAYS a markdown file. Use exactly this structure:

```markdown
# Design-Time Audit: <skill name>
## 1. Executive summary        — the one-paragraph verdict + the headline ratio (what % of the skill is D/R vs S/F)
## 2. What this skill is        — 2–4 paragraphs: the skill's shape, its pipeline, its existing artifacts
## 3. Capability inventory & classification — the full table: capability | where it lives | class | confidence | justification
## 4. The design-time / runtime line — prose: where the line falls and why; the structural observations
## 5. Resource File specifications — one subsection per Resource File (purpose/shape/source/freshness/storage/consumer)
## 6. Runtime architecture sketch — the Cloudflare mapping + failure posture
## 7. Gaps and risks            — the register from Pass 5
```

## Deliverable 2 — the Forward Strategy

ALWAYS a separate markdown file. Use exactly this structure:

```markdown
# Forward Strategy: productizing <skill name>
## 1. The product thesis        — what the productized version is, who uses it, what the Claude design-time session becomes
## 2. Phased build plan         — phases from Pass 6, each with: goal, what ships, primitives used, exit criteria
## 3. The design-time sessions  — the Claude sessions that author each Resource File: inputs, method, outputs
## 4. Runtime AI brief          — exactly what Scout is asked to do, the prompts' shape, the validation wrapped around it
## 5. What stays with Claude    — the F/H residue and how it's surfaced (API escape hatch, human review, or simply 'this remains a service Chris delivers')
## 6. Decision points           — the 2–4 genuine forks the owner must choose between, with a recommendation each
```

## Tone and honesty rules

- Numbers in the report come from the inventory, not vibes. The "headline
  ratio" is a count of classified capabilities, stated as such.
- Never inflate the S-class. If Scout would do a capability *badly*, say so
  and either fatten the Resource File or keep it F/H. An audit that flatters
  the cheap model produces a product that embarrasses the expert.
- Credit what the audited skill already got right — existing deterministic
  scripts, gates, and compiled artifacts are decomposition work already done;
  the strategy should build on them, not re-litigate them.
- Where the audited skill embeds a human correction loop, check usage before
  classifying it. If real runs exercise it, preserve it as class-H on the
  critical path. If real runs skip it (the common case), keep it as an
  **offered surface** — a review/annotate affordance, a publish toggle, a
  regenerate-with-notes loop — rather than a pipeline gate. The cheapest
  honest protection is usually "nothing publishes until the owner flips it
  live," which preserves zero-touch building while keeping a human's name
  protected by a human's read.
- When an audit revises a prior audit, say what changed and why, at the top.
  A classification overturned by evidence is the method working; hide it and
  the method stops working.
