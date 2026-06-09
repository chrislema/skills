#!/usr/bin/env python3
"""Design-document emitter. Sibling to engine.py: same SPEC is the source, but
this compiles the human-readable framework walkthrough (markdown) instead of the
runnable HTML. The expert reads/corrects THIS; recognition over generation.

Everything is derived from the spec. A handful of OPTIONAL editorial fields let
the spec carry annotations the structure can't infer:
  - question.reads     short label of what the item measures   (heading suffix)
  - question.catches   the failure mode it detects             (one-liner)
  - axes.<axis>.label   used for any non-self/team (benchmark) axis group
  - design_notes.thesis            list[str]  -> the §0 framing (has a default)
  - design_notes.benchmark_note    str        -> intro to the benchmark axis group
  - design_notes.woven_not_scored  list[str]  -> §7 "texture, not a dimension"
  - design_notes.corrections       list[str]  -> §7 extra "yours to correct" items

Scope mirrors engine.py: the two-strand-quadrant reference pattern (axes self/team,
quadrants aligned/lone/martyr/grinder). Generalize alongside the engine resolver
for richer address schemas."""
import json, sys

# fixed quadrant semantics of the reference pattern: (self, team) hi/lo
QUAD = {"aligned": ("high", "high"), "lone": ("high", "low"),
        "martyr": ("low", "high"), "grinder": ("low", "low")}

DEFAULT_THESIS = [
    "A stuck company is lost in a mall: until it knows *where it is*, no map and no advice land. The assessment's only job is to place an honest **dot** — right even when that's inconvenient, never flattering its way toward \"you need help.\"",
    "**Dot before map before directions.** Locate first; prescribe last.",
    "**The gap is the product.** A dot alone is trivia; the motivating thing is the distance between where they are and a benchmark they don't control.",
    "**Behavior, not self-rating.** Every question asks what *happens*, never \"how good are you at X\" — a behavior question hides its own right answer, so the gap can't be gamed shut.",
]


def reachable(spec):
    """Enumerate the reachable address set (quadrant|band). Mirrors engine.py."""
    def counts(n):
        d = {0: 1}
        for _ in range(n):
            nd = {}
            for s, c in d.items():
                for f in range(1, 6):
                    nd[s + f] = nd.get(s + f, 0) + c
            d = nd
        return d
    sN, tN = spec["axes"]["self"]["items"], spec["axes"]["team"]["items"]
    thr = spec["scoring"]["quadrant"]["threshold"]
    B = spec["scoring"]["bands"]
    out = set()
    for ss in counts(sN):
        for ts in counts(tN):
            s, t = ss / sN, ts / tN
            sH, tH = s >= thr, t >= thr
            q = "aligned" if (sH and tH) else "lone" if (sH and not tH) else "martyr" if (not sH and tH) else "grinder"
            m, g = (s + t) / 2, abs(s - t)
            c = B[q]
            band = (c["high"] if m >= c["cut"] else c["low"]) if c["measure"] == "mean" else (c["high"] if g >= c["cut"] else c["low"])
            out.add(f"{q}|{band}")
    return out


def stage_of(x, cuts):
    i = 0
    for cut in cuts:
        if x >= cut:
            i += 1
    return i


def doc(spec):
    A = spec["axes"]
    sL, tL = A["self"].get("label", "Self"), A["team"].get("label", "Team")
    thr = spec["scoring"]["quadrant"]["threshold"]
    qd = spec["content"]["quadrants"]
    notes = spec.get("design_notes", {}) or {}
    L = []
    title = spec.get("meta", {}).get("title", "Assessment")

    # ---- header + §0 ----
    L += [f"# {title} — Design Document", "",
          "*The framework behind the assessment, laid out flat so you can read every part at once — no need to traverse the paths by answering questions. This is the thing to correct: mark up anything cut at the wrong joint and the working assessment regenerates from the same spec.*", "",
          "---", "", "## 0. The one idea everything hangs on", ""]
    for t in (notes.get("thesis") or DEFAULT_THESIS):
        L.append(f"- {t}")
    L.append("")

    # ---- §1 the 2x2 ----
    L += ["---", "", "## 1. The 2×2 — where the dot sits", "",
          f"Two axes, each scored 1–5; the line between low and high is **{thr}**. Where they diverge, the divergence is itself the finding.", "",
          "| Axis | Label shown | What it reads |", "|---|---|---|",
          f"| Self | **{sL}** | the hands-on / individual capability axis |",
          f"| Team | **{tL}** | the organizational / system axis |", "",
          "```"]
    w = max(13, *(len(qd[k]["name"]) for k in QUAD)) + 1
    bar = "─" * (w + 1)
    pad = lambda s: f"{s:<{w}}"
    L += [f"                 {tL}",
          f"                 LOW{' ' * (w - 1)}HIGH",
          f"            ┌{bar}┬{bar}┐",
          f"       HIGH │ {pad(qd['lone']['name'])}│ {pad(qd['aligned']['name'])}│",
          f"  {sL[:9]:<9} │ {pad('self↑ team↓')}│ {pad('self↑ team↑')}│",
          f"            ├{bar}┼{bar}┤",
          f"       LOW  │ {pad(qd['grinder']['name'])}│ {pad(qd['martyr']['name'])}│",
          f"            │ {pad('self↓ team↓')}│ {pad('self↓ team↑')}│",
          f"            └{bar}┴{bar}┘",
          "```", "",
          "| Quadrant (key) | Name shown | Condition | The line it opens with |",
          "|---|---|---|---|"]
    cond = {"aligned": f"{sL} high · {tL} high", "lone": f"{sL} high · {tL} low",
            "martyr": f"{sL} low · {tL} high", "grinder": f"{sL} low · {tL} low"}
    for k in ("aligned", "lone", "martyr", "grinder"):
        op = qd[k]["opener"][0].replace("|", "\\|")
        L.append(f"| `{k}` | **{qd[k]['name']}** | {cond[k]} | {op} |")
    L += ["",
          f"The two **off-diagonal** cells — *{qd['lone']['name']}* ({sL} without {tL}) and *{qd['martyr']['name']}* ({tL} without {sL}) — are where the diagnosis is most alive: each names an imbalance the company usually can't see in itself.", ""]

    # ---- §2 lifecycle ----
    LC = spec["scoring"].get("lifecycle")
    if LC:
        stages = LC["stages"]
        cuts = LC["cuts"]
        ms = {s.get("name"): s for s in (spec.get("maturity_stages") or [])}
        ms_list = spec.get("maturity_stages") or []
        L += ["---", "", "## 2. The lifecycle model — how far along", "",
              "The 2×2 reads the *shape* of stuckness; a separate, independently-measured read says *how far along* the company is. Five stages, cut where the transition is what the expert is paid to move people through. Each carries both faces — the new problem that appears and the mastery that deepens.", "",
              "| # | Stage | Problem face | Mastery face |", "|---|---|---|---|"]
        for i, nm in enumerate(stages):
            m = ms.get(nm) or (ms_list[i] if i < len(ms_list) else {})
            L.append(f"| {i+1} | **{nm}** | {m.get('problem_face','—')} | {m.get('mastery_face','—')} |")
        L += ["",
              f"The dot's **achieved stage** comes from the *(self + team) ÷ 2* mean, binned at cut points `{' / '.join(str(c) for c in cuts)}` on the 1–5 scale.", ""]

    # ---- §3 instrument ----
    qs = spec["questions"]
    L += ["---", "", "## 3. The instrument — the questions, and what each reads", "",
          f"{len(qs)} questions. Every option ladder runs **worst → best**; the score is the option's position (1–5). In the live assessment options are shuffled per session so position never leaks the good answer; here they're in rung order so you can see the ladder.", ""]
    # group: self, team, then any other axes (benchmark)
    axis_order = ["self", "team"] + [a for a in dict.fromkeys(q["axis"] for q in qs) if a not in ("self", "team")]
    for ax in axis_order:
        items = [q for q in qs if q["axis"] == ax]
        if not items:
            continue
        if ax == "self":
            head = f"### {sL} (self axis) — {len(items)} items"
            intro = ""
        elif ax == "team":
            head = f"### {tL} (team axis) — {len(items)} items"
            intro = ""
        else:
            lbl = A.get(ax, {}).get("label", ax.title())
            head = f"### {lbl} ({ax} axis) — {len(items)} items, *not* part of the 2×2"
            intro = notes.get("benchmark_note", "These set the benchmark for the normative gap in §5. They're deliberately factual, not evaluative — a matter of record, not opinion, which is what makes the benchmark one the respondent doesn't control.")
        L += [head, ""]
        if intro:
            L += [intro, ""]
        for q in items:
            reads = q.get("reads")
            catches = q.get("catches")
            hdr = f"**{q['id']}"
            hdr += f" — {reads}.**" if reads else ".**"
            if catches:
                hdr += f" *Catches:* {catches}"
            L.append(hdr)
            L.append(f"> \"{q['stem']}\"")
            for i, opt in enumerate(q["options"], 1):
                L.append(f"> {i}. {opt}")
            L.append("")

    # ---- §4 scoring variables ----
    B = spec["scoring"]["bands"]
    addrs = sorted(reachable(spec))
    L += ["---", "", "## 4. The scoring variables — what holds the dot in place", "",
          "The address every respondent resolves to has two independent components. \"Independent\" is load-bearing: if the depth read came from the same numbers that drew the quadrant, it would add no information.", "",
          "| Variable | How it's computed | What it captures |", "|---|---|---|",
          f"| **Quadrant** | self ≥ {thr}? and team ≥ {thr}? | the *shape* of stuckness (one of four) |",
          "| **Band (depth)** | see below | *how far into* that shape |"]
    if LC:
        L.append("| **Journey / commitment** | mean of the benchmark items (separate questions) | the benchmark for the normative gap (§5) |")
    L += ["", "The band forks on a *different* quantity than the one that placed the quadrant:", ""]
    diag = [k for k in ("aligned", "grinder") if k in B and B[k]["measure"] == "mean"]
    offd = [k for k in ("lone", "martyr") if k in B and B[k]["measure"] == "gap"]
    if diag:
        L.append(f"- **On-diagonal** ({', '.join(qd[k]['name'] for k in diag)}) — axes agree, so depth forks on **shared altitude** (the mean):")
        for k in diag:
            c = B[k]
            L.append(f"  - `{k}`: mean ≥ **{c['cut']}** → *{c['high']}*, else → *{c['low']}*")
    if offd:
        L.append(f"- **Off-diagonal** ({', '.join(qd[k]['name'] for k in offd)}) — the imbalance is the point, so depth forks on the **size of the gap** between axes:")
        for k in offd:
            c = B[k]
            L.append(f"  - `{k}`: gap ≥ **{c['cut']}** → *{c['high']}*, else → *{c['low']}*")
    L += ["", f"That yields **{len(addrs)} addresses**, each with its own authored landing:",
          "`" + "`, `".join(addrs) + "`.", ""]

    # ---- §5 gaps ----
    L += ["---", "", "## 5. The gaps — the engine of the whole thing", "",
          "A gap is always *your answer vs. a fixed point you don't control* — the second half is what keeps it honest.", ""]
    corr = [k for k in qd if qd[k].get("gap_family") == "correlational"]
    vfirst = [k for k in qd if qd[k].get("validate_first") and qd[k].get("gap_family") == "none"]
    if corr:
        L += ["### Gap A — Correlational (between your own two axes)",
              f"The two axes should track together; a mature company has both. When they diverge, the divergence is the finding and the benchmark is your *other* answer. This headlines the off-diagonal results: " +
              "; ".join(f"**{qd[k]['name']}** ({'self above team' if QUAD[k]==('high','low') else 'team above self'})" for k in corr) + ".", ""]
    if vfirst:
        L += ["The on-diagonal results " + " and ".join(f"**{qd[k]['name']}**" for k in vfirst) +
              " have no axis-divergence to lean on, so they **don't manufacture a gap** — they validate and point at a next step instead. Forcing a gap on a both-low company only demoralizes; forcing one on a both-high company only flatters. (The honesty rule, made mechanical.)", ""]
    nrm = spec.get("content", {}).get("normative")
    if LC and nrm:
        stages = LC["stages"]
        bb = spec["scoring"].get("normative", {}).get("behind_by", 1)
        ex = (nrm.get("behind", "")
              .replace("{committed}", stages[min(3, len(stages)-1)])
              .replace("{achieved}", stages[1] if len(stages) > 1 else stages[0])
              .replace("{quadrant}", qd.get("martyr", {}).get("name", "")))
        L += ["### Gap B — Normative (capability vs. commitment) — the headline for the stuck middle",
              "The lifecycle bar shows two markers: the **achieved stage** (from the two axes) and the **committed stage** (from the separate commitment questions). When commitment sits "
              f"**{bb}+ stage{'s' if bb!=1 else ''} ahead** of capability, the report names it directly:", "",
              f"> *{ex}*", "",
              "That's the \"we pay for it / we've been at this a year — why are we still here?\" pain, computed rather than asserted. Level reads *on track*; capability ahead of investment reads *ahead*.", ""]

    # ---- §6 report assembly ----
    vmax = max((len(qd[k].get("opener", [])) for k in qd), default=1)
    L += ["---", "", "## 6. How scores + gaps become the report", "",
          "The report reads as one continuous, written-to-you piece, but nothing is generated live — it's assembled from pre-authored, pre-approved parts. The address (§4) selects which parts drop in.", "",
          "```",
          "FIXED SKELETON  (same arc every time; every transition authored once)",
          "  the dot → the live problem → what becomes possible → where to point first → close",
          "        │",
          "        ▼   slots filled from the atom library, keyed to the address",
          f"  ├─ Opener      ← 1 of {vmax} phrasings per quadrant, picked by a stable per-session hash",
          f"  ├─ Depth lead  ← 1 line per full address ({len(addrs)} of them)",
          "  ├─ Body        ← the per-quadrant diagnostic paragraphs",
          "  ├─ 2×2 + dot   ← marker placed from the raw axis means"]
    if LC:
        L.append("  └─ Lifecycle   ← the stage bar + the normative gap sentence (behind / on-track / ahead)")
    L += ["```", "",
          "So the moving parts: the **quadrant** picks name + opener + body; the **band** picks the one-line depth lead; the **dot** is plotted continuously from the exact means (the plot never out-resolves the prose); "
          + ("the **gap** sentence is driven by the separate commitment questions. " if LC else "")
          + f"Two-plus phrasings per opener chosen by a per-session hash give two identical addresses a slightly different read — the 1-of-1 feel with no live generation. Advice stays at the level of **intent, not tooling**, so the diagnosis doesn't go stale as tools churn.", ""]

    # ---- §7 yours to correct ----
    L += ["---", "", "## 7. What's yours to correct", "",
          "The joints cut from the brief, not from inside your head — the ones most likely to be slightly off:", "",
          f"1. **The two axes.** Is *{sL} × {tL}* the right split, or is the real fault line elsewhere?",
          f"2. **The four names.** Will a leader say \"we're {qd['martyr']['name']}\" / \"we're {qd['grinder']['name']}\" out loud, or do any land as an insult they bounce off?"]
    n = 3
    if LC:
        L.append(f"{n}. **The {len(LC['stages'])} stages and their names** ({', '.join(LC['stages'])}) — right joints? right words?"); n += 1
        L.append(f"{n}. **The headline gap.** Is *capability-vs-commitment* the one to lead with, or the {sL}/{tL} imbalance?"); n += 1
    sm = spec.get("stuck_map") or spec.get("stuck_points") or []
    if sm:
        L.append(f"{n}. **The causes in the body copy.** Did any *cause* land in the wrong place? e.g. \"{sm[0].get('symptom','—')}\" attributed to: {sm[0].get('cause','—')}."); n += 1
    for c in (notes.get("corrections") or []):
        L.append(f"{n}. {c}"); n += 1
    woven = notes.get("woven_not_scored") or []
    if woven:
        L += ["", f"Currently **woven into the copy as texture rather than scored**: {', '.join(woven)}. If any should become its own measured dimension, that's the next thing to build."]
    L += ["", "Tell me what's wrong in plain language and I'll edit the spec and recompile — this document and the working assessment both regenerate from the same source.", ""]
    return "\n".join(L)


def main():
    if len(sys.argv) < 2:
        print("usage: design_doc.py spec.json [out.md]"); sys.exit(2)
    spec = json.load(open(sys.argv[1]))
    out = doc(spec)
    if len(sys.argv) >= 3:
        open(sys.argv[2], "w").write(out)
        print("Emitted:", sys.argv[2])
    else:
        print(out)


if __name__ == "__main__":
    main()
