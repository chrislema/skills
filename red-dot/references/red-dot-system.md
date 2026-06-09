# Red Dot — The Build System

*Operational companion to `vision.md`. The vision document argues **why** a custom diagnostic works (dot before map before directions; the gap is the product). This document states the **system that builds one** — the eight skills, the contracts between them, the techniques they share, the gates that make them a system rather than a sequence, and the architecture that turns all of it into something a generator can run and a checker can refuse to ship broken.*

---

## 0. What the system is

Red Dot manufactures, for a domain expert, the diagnostic instrument their non-expert customers need before they can hear advice. A build takes the expert's tacit model and produces a complete, self-hostable assessment: a lifecycle map, a 10–15 question instrument, deterministic scoring, and a rich report that locates the customer, names the gap that moves them, and points toward the expert's offer.

The system is **eight skills arranged as a dependency chain**, drawing on a **small shared kit of techniques**, held together by a set of **mechanically checkable invariants** wired onto the seams between skills. The intelligence is spent once, at design time, authoring a bounded space; runtime is deterministic traversal of a compiled artifact. The defining architectural move, hardened below, is that the compiled artifact is described by a **declarative spec** that is the single source of truth — an engine generates the deliverable from it, and a checker gates that generation, so a failing artifact cannot be produced.

What follows is the system as it stands after being stress-tested end to end against a working reference instrument (the Alignment Mirror). Where something is proven, it is stated plainly. Where it has been demonstrated in principle but not exercised on a hard case, that is marked.

---

## 1. The spine (the minimum thesis the skills depend on)

Three load-bearing claims from the vision doc, compressed to what the skills need:

**The sequence is fixed: dot before map before directions.** A customer who doesn't know where they are can't use a map or follow directions. The whole instrument exists to place an honest dot first.

**The gap is the product.** A report turns on the distance between the respondent's answer and a **benchmark they don't control**. That second clause is the entire trick — it is what makes the gap honest rather than a self-rating in disguise. There are three benchmark families, all available from a single respondent: the **normative** gap (where tenure/stage says you should be vs. where you operate), the **predictive** gap (where a model said you'd struggle vs. where you do), and the **correlational** gap (where two of your own answers should track but diverge). Single-respondent honesty is a solved discipline, not an open problem: the benchmark belongs to the *comparison*, not to a second person.

**Behavior, not self-report.** The instrument elicits observable events, not ratings of inner states, because behavior carries its own benchmark (the work stalled or it didn't) and hides its own scoring (the respondent can't tell which answer is the flattering one). This is what makes every gap both measurable and honest.

Everything below serves these three.

---

## 2. The eight skills and their contracts

A system, as distinct from a person who happens to be fast, is a fixed schema plus a defined process for filling it. The schema is a chain of artifacts, each derived from and consistency-checked against the prior:

```
positioning_brief → case_intake → model_induction → outcome_space
→ instrument → scoring_spec → content_library → assembly
```

Each skill is defined by its contract: what it **consumes**, what it **produces**, and what it **owes** the rest of the system. The "owes" clauses are not aspirations — every one of them is a checkable assertion enforced at a seam (Section 4).

**0 · Positioning** — *the offer-first cut.* Consumes the expert's offer, who buys, and which transition they are paid to move customers through. Produces a brief: customer, offer, the transitions worth money, and the voice/banned-phrase list. Owes: the joints the map will be cut at (Skill 2) and the voice constraints (Skill 6). This is a commercial read, deliberately separate from the epistemic intake that follows. Skip it and everything downstream can be beautiful and still lead to no sale.

**1 · Case intake** — *the concrete past-tense walk, fenced from abstraction.* Consumes the brief plus raw seed (the expert's posts, notes, talks). Produces a bank of real client cases, each tagged symptom-observed / cause-actual / misdiagnosis, using Critical-Decision-Method probes (what did you notice first, what was actually wrong, what would a novice have thought). Owes: cases must be concrete and **untyped** — the skill is structurally forbidden from proposing a stage or pattern, because the model's default failure mode is leading the witness.

**2 · Model induction** — *seed, then render the draft deliberately wrong.* Consumes the case bank and brief. Produces the `lifecycle_model` (5 stages, rarely 6, each carrying both faces — the new problem-surface and the deepening mastery — plus a say-it-out-loud name) and the `stuck_map` (transition failures by boundary, each typed by locus: capability hole / capability currency / value collapse / segment-and-courage, depth-ranked, with tenure as a prior over locus). The method is to show the expert a maximally-correctable draft and harvest the correction, because correction is a higher-bandwidth channel than generation. Owes: every stage boundary maps to something in the offer. Its acceptance test is not "do you like this map" but **"does this map drop your real clients where you would"** — case-grounding, the same move the scoring uses.

**3 · Outcome-space design** — *choose the gap, then set the resolution.* Consumes the model and stuck_map. Produces the **address schema** (the coordinate every respondent resolves to — e.g. stage × locus × theme × gap-state) and the **chosen gap with its benchmark source**. This is the single most consequential skill in the chain, because it sets what the report can honestly say. Two coupled methods live here: *gap-family matching* (pick the benchmark whose geometry fits the cell — a correlational gap needs divergence, so a both-agree cell needs a normative one or an honest non-gap) and *the resolution dial* (fork on what scoring already computes, per-region on the dimension that actually varies, and recognition-test each fork for whether the reader would feel it). Owes: the exact set of addresses that must have landings (Skill 6), and the list of things that must be discriminable (Skill 4).

**4 · Instrument authoring** — *ask the symptom, hide the rung.* Consumes the address schema (what must be told apart) and stuck_map (what must be detectable). Produces 10–15 questions, each tagged to the axis or theme it feeds, behaviorally concrete, options in rung order. Three hard rules: never ask people to rate the variable they can't perceive (ask symptoms, infer the cause); kill social desirability at both levels — position (shuffle) and content (forced choice where no option is the trophy); reach for the **three-tense pattern** (have-done / doing-now / do-consistently) whenever trajectory matters, because it manufactures a correlational gap for free. Owes: every stuck point detectable by at least one question; no orphan questions.

**5 · Scoring spec** — *a total function to an address.* Consumes the instrument and address schema. Produces a deterministic map from every possible answer pattern to a valid address, computing the gaps along the way. Owes: **totality** (every pattern resolves) and **bijection-readiness** (it may never emit an address that Skill 6 didn't author). Owns the **exemplar test**: run three or four people whose answer you already know and confirm the math lands them right.

**6 · Content authoring** — *write each atom against the address that selects it, never beyond.* Consumes the address schema, model, stuck_map, and voice constraints. Produces an authored landing for every reachable address: a fixed skeleton that carries the flow, stage/locus atoms that drop into its slots, interaction cells that speak to combinations, and variant banks (two or three phrasings per atom) so identical addresses still read differently. Owes: coverage, the honesty gate, the voice gate, and — for any claim — binding to a scored input (no unmeasured assertion, including the quiet kind: claims about a respondent's *history* the instrument never measured).

**7 · Assembly** — *compile, gate, emit.* Consumes the instrument, scoring spec, and content library. Produces the artifact. Owes: bijection verified at compile (reachable addresses equal authored landings) and a full invariant lint that **must pass before anything is emitted**. The assembler refusing to emit is the system's last gate.

A note on direction: the chain is mostly forward, but **Skills 1 and 2 form a loop** — the cases the expert reaches for while correcting the wrong draft *are* the intake, flowing out of the disagreement in one motion. Intake and induction interleave in real time even though they stay structurally separate.

---

## 3. The kit — the techniques the skills share

The eight skills are not eight inventions. They draw on a handful of techniques, several of which appear in more than one skill. Naming the kit once is what makes the system cohere rather than read as eight bolted-together tricks.

**Gap against an uncontrolled benchmark** runs through three skills: it is how Skill 3 diagnoses the customer, how Skill 2 elicits from the expert (espoused theory gapped against real cases), and how Skill 0 cuts the map (the offer is the benchmark the stages are cut to).

**Behavior over self-report** is the same move aimed at two different people: walk the expert's cases (Skill 1), ask the customer about observable symptoms (Skill 4).

**Recognition over generation** drives Skill 2's correction-as-elicitation, Skill 3's is-this-fork-perceptually-real test, and Skill 5's "Bob is obviously a stage 2." Experts can't reliably generate their tacit model, but they recognize a right or wrong one instantly — which means the expert need only be a *recognizer*, not a world-builder, and a brilliant practitioner who is a poor articulator can still have a rigorous instrument built.

**Case-grounding (the exemplar test)** is one case-set doing double duty: it accepts the map in Skill 2 ("does this drop your clients where you would") and calibrates the scoring in Skill 5.

**Author the pairwise (interaction cells)** is one mechanism used twice — diagnosis combinations in Skill 6, and the ranking rationale one layer out. Most pairwise spaces are small and most cells prune before authoring, so combinatorial richness is the product, not a threat to manage.

**The three-tense pattern** lives in Skill 4 but its job is to manufacture the correlational gap Skill 3 consumes — so it is the seam between the instrument and the diagnosis.

The deepest version of the coherence claim: a single **gap-pattern vocabulary** — a finite, named set of spreads like *proven-but-dormant* or *burst-without-base* — is the join key across three skills at once. The instrument measures the spread, the diagnosis headlines it, and the ranking rationale is keyed to it. When the same small vocabulary is the spine of the questions, the dot, and the advice, the assessment reads as one intelligence. That coherence is what makes the output feel expert.

---

## 4. The gates — invariants on the seams

Validation is not a final step. It is a **standing checker wired onto the seams**, run before any artifact is emitted, and it is what makes this a system rather than a careful sequence. Each invariant is mechanically checkable, and each catches a specific skill's characteristic failure — often at a seam far from where the failure originated (a Skill-3 over-resolution surfaces as a Skill-6/7 bijection failure; the gate catches it regardless of origin).

Gates carry one of three severities:

- **BLOCK** — must pass or the assembler refuses to emit.
- **ADVISORY** — reported every run, non-blocking at the current tier, tracked rather than silenced.
- **N/A** — not applicable until the spec gains the structure the gate checks (see Section 6, tier-awareness).

The blocking set:

| Gate | What it asserts | Catches |
|---|---|---|
| **Coverage** | every reachable address terminates in an authored landing | over-resolution; orphan scores |
| **Bijection** | reachable addresses equal authored landings (no orphans either way) | Skill-3/5/6/7 drift |
| **Gap present** | every address leverages a *measured* benchmarked gap **or** is a declared *validate-first* cell — and none leans on an *unmeasured implied* benchmark | a report with nothing to motivate movement; a self-rating in disguise |
| **Evidence** | every claim is backed by a scored input — including no unmeasured-*history* claims ("used to," "stopped," "drifted") | content asserting beyond what was measured |
| **Voice gate** | banned phrases and internal jargon never reach the customer | the "here's the thing…" / "nobody talks about" reveal family |
| **No orphan questions** | every question feeds the stage axis or a named theme | instrument padding |
| **Honesty gate** | no path is forced to conclude "buy the thing" | a rigged map |

Three refinements the system earned in testing are worth stating explicitly:

The **gap-present gate encodes the commercial asymmetry.** Not every cell must be gapped. A both-low/early cell is the *validate-first* analog of stage 1 — you validate and stabilize, you do not manufacture a divergence that isn't there, and you never assert a "you should be further" baseline you didn't measure. That last clause is the real teeth: leaning on an *unmeasured implied* benchmark is the precise "self-rating in disguise" failure the gate exists to stop.

The **evidence gate includes a temporal-claim lint.** The common way prose drifts beyond the data is not invented statistics but quiet history: "you've drifted from," "you stopped." These read as insight and rest on nothing the instrument measured. A standing lint catches the class; inspection misses it case by case.

The gates that depend on advanced structure — **detectability, commercial closure, two-faced coverage, ranking-gap-derived, positional rationale** — are N/A until the spec contains a stuck_map, an offer, maturity stages, or a ranking, at which point they activate as BLOCK. The checker keys severity off *spec presence*, not a tier flag, so it scales without modification.

---

## 5. The architecture — design-time AI, deterministic runtime

A bounded assessment has a property the whole architecture rests on: **the input space is fully knowable in advance.** Fixed questions, enumerable answers, an enumerable address space. If you know everything the input can be, you know everything the output should ever say — so it can all be written ahead of time. That collapses "how do we generate rich, personal, flowing output" into "how do we author the space and select from it deterministically." AI is the right tool for the first half and the wrong tool for the second.

So the bet is **design-time AI, deterministic runtime.** AI runs once, to draft the lifecycle, questions, scoring rationale, and every piece of report content across the coherent path space. The output is a *compiled artifact*: banks of authored content keyed to score-addresses. Runtime is pure traversal. This buys auditability (every word was authored and approved once; nothing is improvised in front of a customer), a lightweight stack (no inference at request time), and speed of production.

The artifact reads as bespoke without being generated because of one principle: **deterministic but rarely repeated.** The address space is large enough that two customers rarely land on the same assembled whole, yet every landing is fixed and pre-approved. Variant banks add the final touch — the same address reads differently across sessions by a stable per-session selection, with no model in the loop.

### Spec / engine / checker

The architecture has three parts, and the relationship between them is the system's most important property:

- **The spec** is the single source of truth — a declarative description of the whole assessment: questions with their tags, the scoring rule, the address space, the content bank with its variants and gap-family tags, the banned list, and (as they appear) the stuck_map, offer, stages, and ranking.
- **The engine** compiles the spec into the deliverable: it resolves the reachable address set, composes every landing, and renders the artifact as pure functions of the spec.
- **The checker** validates the compiled surface against the invariants and **gates emission**.

Because the engine compiles the *same spec* the checker validates and the artifact is rendered from, **the three cannot disagree.** This closes the one hole that exists when a spec is hand-extracted to describe a hand-built artifact: the two can drift, and a green check on the spec no longer guarantees a clean artifact. When the spec is the source, drift is not caught after the fact — it is structurally impossible, because a failing spec produces no artifact at all.

This is also the seam a **generator** slots into. A generator emits the spec; the checker validates it; the engine compiles it. The system does not require a human to assemble the artifact — only to supply the irreducible judgment (Section 7) that the spec encodes.

---

## 6. The tier ladder

The same architecture scales from a single file to a fenced runtime weaver. Three rungs, chosen by how much capture, richness, and prose-continuity the situation needs. The ladder is also the build order: ship the floor to validate the model and the dot, then climb only as far as the goal requires.

- **Tier 0 — the static mirror.** One self-contained HTML file. Instrument, scoring, dot, and a small set of authored reports inline; results compute in memory and display, never persist. The lightest funnel-top object there is — shareable, instant. Deliberately coarse; it plants the dot and gets passed around. The first upgrade off this rung is almost never more questions — it is more *resolution*: fork the prose on the gap and level the scoring already computes.
- **Tier 1 — the precomputed engine (the default).** The spec/engine/checker architecture of Section 5, served on a light edge stack (static front end, edge functions, key-value storage). The instrument can branch; scoring resolves to a full address; the report composes at request time from authored atoms, interaction cells, and variant banks; sessions persist; the email gate and offer bridge are present. **Zero model in the hot path** — the model ran at design time. This is where most builds should live.
- **Tier 2 — the fenced weave (the justified exception).** Everything in Tier 1, plus a runtime model that weaves the prose for a surface that must read as one continuous arc *and* is too voice-varied to atomize cleanly. It buys cohesion at the cost of a surface no gate can fully check — a fluency guard catches jargon and a fabrication guard catches invented facts, but neither can verify that a *claim is true*. The diagnosis stays Tier-1 deterministic; only the prose is woven. Quarantine it behind explicit gates and justify it per surface.

How each skill behaves across the rungs (the resolution dial is the through-line — coarse at T0, fine at T1, same address with woven prose at T2):

| Skill | Tier 0 | Tier 1 | Tier 2 |
|---|---|---|---|
| 0 Positioning | skipped / implicit | real brief; activates commercial-closure gate | unchanged |
| 1 Case intake | generic borrowed model | real CDM case bank | unchanged (design-time) |
| 2 Model induction | generic 2-axis quadrant | induced lifecycle + stuck_map with locus | same model |
| 3 Outcome-space | coarse address | fine address; branching | same address |
| 4 Instrument | flat, fixed | adaptive / branching | unchanged |
| 5 Scoring | inline | declared spec → address | still deterministic |
| 6 Content | whole reports | skeleton + atoms + interaction cells + variants | atoms + fenced weaver for one surface |
| 7 Assembly | one hand-assembled file | engine compiles spec → artifact, gate-on-emit | engine + fenced model |

The corrected understanding the ladder makes precise: for a bounded assessment there is **no hard capability line that forces a runtime weaver.** A runtime model isn't buying a capability you otherwise couldn't get — it's buying you out of authoring the space, paid for with the one thing it can't give back: a gate-checkable surface. And that convenience-margin shrinks every month, because design-time AI is exactly what makes authoring the space cheap.

---

## 7. What stays human

AI collapsed the *production* time. It did not collapse the *expertise.* The moat is the expert's judgment; AI is the printing press. The system isolates the judgment that does not automate, and the spec is where it gets encoded:

1. **Choosing the gap and sourcing its benchmark** — which gap headlines the report, and what fixed point the respondent doesn't control it is measured against. The most consequential single choice in the design, because it sets what the report can honestly say.
2. **Discernment** — which dimensions matter, what the meaningful gradations are, and how to phrase a question about a thing the customer can't perceive.
3. **Resolution** — at what granularity a fork produces a difference the reader will actually feel; and the matching discipline that the visualization must not out-resolve the prose.
4. **Pruning the impossible** — deciding which stage × locus × interaction cells can't exist. The map of the impossible is as much expertise as the cells that are filled.
5. **Naming** — stages and results, for motivation, memorability, and shareability. The difference between a stage someone says out loud and one they don't.
6. **The honesty gate** — the standing commitment that the dot must be honest even when inconvenient; not every path may land on "you need my thing."

---

## 8. Status — proven, and open

**Proven end to end.** The eight skills, their contracts, the kit, the gate machinery, and the spec/engine/checker architecture have been exercised through a full build-and-harden cycle against a working reference instrument. The engine generates the artifact deterministically, the checker refuses to emit on any blocking failure, drift is structurally prevented, and the gates activate correctly as the spec gains structure.

**Demonstrated in principle, not yet on a hard case.** The reference instrument is a two-axis quadrant with no offer. The machinery that only appears at full Tier 1 — an *induced* lifecycle and stuck_map with locus (Skills 1–2 ran on a borrowed generic model), a branching instrument, interaction cells across a genuine theme dimension, and a gap-derived ranking — has slots and gates ready but has not been *produced* by the skills against a real domain. The natural next step is to run the same build against a domain that has real stages and an expert with an offer, and see whether the skills hold or reveal new seams.

**Open by design, not by oversight.** Everything the system validates, it validates at *build* time. A compiled, deterministic instrument places an honest dot at ship, grounded in cases — but it has no live loop to learn it misplaced a stranger six months on. This is true of every instrument that maps people, and the mitigations are all design-time (the exemplar test, synthetic-cohort validation, the case-grounded acceptance test). A live feedback channel could be added later but would trade away determinism, so it stays out of the core by choice. The couple/team variant — a second respondent as one more uncontrolled benchmark — is an advanced layer on the single-respondent default, not a dependency.

**How the system stays a system.** It is built and maintained breadth-first: each revision pass touches all eight skills at once, deepening each while keeping the seams honest, rather than perfecting one skill in isolation until it no longer hands the next what it needs. A snapshot regenerated from the current skills, run through the gates, is the integration test for each pass — and the cost of producing that snapshot is itself the diagnostic. When it is cheap and automatic, the skills are a system. When it is laborious and manual, they are still a person who happens to be fast.

---

*The shape of the whole: every report turns on a gap between the respondent's answer and a benchmark they don't control; behavior is what makes that gap both measurable and honest; the gap, the map, the prose, and the ranking are authored exhaustively at design time into a spec that is the single source of truth; an engine compiles that spec to a deterministic artifact light enough to run on the edge; and a checker wired onto the seams refuses to ship anything that breaks an invariant. The customer meets a report that locates them, names the gap that moves them, speaks to their exact combination, points them at the move with the most leverage from where they stand, and rarely repeats — and every word of it was written, and approved, and gate-checked, before they ever arrived.*
