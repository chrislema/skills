#!/usr/bin/env python3
"""Red Dot standing gate-checker. Reads a declarative assessment spec and runs
the §11 invariants mechanically. Severity: BLOCK (must pass to emit), ADVISORY
(reported, non-blocking at this tier), N/A (not applicable at this tier).
Exit non-zero if any BLOCK gate fails — i.e. assembly may not emit."""
import json, sys, re

def reachable_addresses(spec):
    # enumerate the exact reachable address set from the scoring rule
    def counts(n):
        d={0:1}
        for _ in range(n):
            nd={}
            for s,c in d.items():
                for f in range(1,6): nd[s+f]=nd.get(s+f,0)+c
            d=nd
        return d
    sN=spec["axes"]["self"]["items"]; tN=spec["axes"]["team"]["items"]
    thr=spec["scoring"]["quadrant"]["threshold"]; b=spec["scoring"]["bands"]
    addrs=set()
    for ssum in counts(sN):
        for tsum in counts(tN):
            s,t=ssum/sN, tsum/tN
            sH,tH=s>=thr,t>=thr
            q='aligned' if (sH and tH) else 'lone' if (sH and not tH) else 'martyr' if (not sH and tH) else 'grinder'
            mean=(s+t)/2; gap=abs(s-t); cfg=b[q]
            if cfg["measure"]=="mean":
                band=cfg["high"] if mean>=cfg["cut"] else cfg["low"]
            else:
                band=cfg["high"] if gap>=cfg["cut"] else cfg["low"]
            addrs.add(f"{q}|{band}")
    return addrs

def run(spec):
    R=[]  # (gate, severity, status, detail)
    land=spec["landings"]; tier=spec["tier"]
    measured={"correlational"}  # families with a MEASURED benchmark in this spec
    if any(qd["axis"]=="tenure" for qd in spec["questions"]): measured.add("normative")

    # --- BLOCK: Bijection + Coverage ---
    reach=reachable_addresses(spec); authored=set(land.keys())
    dead=reach-authored; orphan=authored-reach
    R.append(("Coverage","BLOCK","PASS" if not dead else "FAIL",
              "all reachable addrs authored" if not dead else f"dead/unauthored: {sorted(dead)}"))
    R.append(("Bijection","BLOCK","PASS" if (not dead and not orphan) else "FAIL",
              f"reach={len(reach)} authored={len(authored)}"+(f" orphan:{sorted(orphan)}" if orphan else "")))

    # --- BLOCK: Gap present (with §13 asymmetry) ---
    gfails=[]
    for a,L in land.items():
        fam=L["gap_family"]; vf=L.get("validate_first",False)
        if fam in measured: continue                 # has a measured gap -> ok
        if vf and fam=="none": continue              # declared validate-first -> ok (honest)
        gfails.append(f"{a}(fam={fam},vf={vf})")      # leans on unmeasured/implied benchmark
    R.append(("Gap present","BLOCK","PASS" if not gfails else "FAIL",
              "every addr has measured gap or is validate-first" if not gfails else f"unbacked: {gfails}"))

    # --- BLOCK: Evidence (claim-to-input; temporal-history lint) ---
    temporal=re.compile(r"\b(used to|stopped|no longer|drifted|any ?more|once (was|did)|back when)\b",re.I)
    aux=spec.get("aux_texts",[])
    efails=[]
    for a,L in land.items():
        hits=temporal.findall(L["text"])
        if hits: efails.append(f"{a}:{[h if isinstance(h,str) else h[0] for h in hits]}")
    for i,t in enumerate(aux):
        if temporal.findall(t): efails.append(f"aux[{i}]")
    R.append(("Evidence","BLOCK","PASS" if not efails else "FAIL",
              "no unmeasured-history claims" if not efails else f"unbacked temporal claim -> {efails}"))

    # --- BLOCK: Voice gate ---
    vfails=[]
    for a,L in land.items():
        for p in spec["banned_phrases"]:
            if p.lower() in L["text"].lower(): vfails.append(f"{a}:'{p}'")
    for i,t in enumerate(aux):
        for p in spec["banned_phrases"]:
            if p.lower() in t.lower(): vfails.append(f"aux[{i}]:'{p}'")
    R.append(("Voice gate","BLOCK","PASS" if not vfails else "FAIL",
              "no banned phrases" if not vfails else f"{vfails}"))

    # --- BLOCK: No orphan questions ---
    oq=[q["id"] for q in spec["questions"] if not q.get("axis")]
    R.append(("No orphan questions","BLOCK","PASS" if not oq else "FAIL",
              f"{len(spec['questions'])} questions, all axis-tagged" if not oq else f"orphans:{oq}"))

    # --- BLOCK: Honesty gate ---
    forced=[a for a,L in land.items() if L.get("forced_cta")]
    R.append(("Honesty gate","BLOCK","PASS" if not forced else "FAIL",
              "no path forced to buy" if not forced else f"{forced}"))

    # --- ADVISORY: Behavioral elicitation ---
    intro=[q["id"] for q in spec["questions"] if not q.get("behavioral",True)]
    R.append(("Behavioral elicitation","ADVISORY","PASS" if not intro else "WARN",
              "all items behavioral" if not intro else f"introspective items: {intro}"))

    # --- ADVISORY: Social desirability (content cue) ---
    cue=[q["id"] for q in spec["questions"] if q.get("content_cue",False)]
    R.append(("Desirability (content cue)","ADVISORY","PASS" if not cue else "WARN",
              "no visible good answer" if not cue else f"{len(cue)}/{len(spec['questions'])} items carry a content cue"))

    # --- Gates that ACTIVATE as the spec gains structure (tier-aware) ---
    qids={q["id"] for q in spec["questions"]}
    sp=spec.get("stuck_points") or []
    if not sp: R.append(("Detectability","N/A","—","no stuck_map at this tier"))
    else:
        und=[s.get("id","?") for s in sp if not (set(s.get("detected_by",[]))&qids)]
        R.append(("Detectability","BLOCK","PASS" if not und else "FAIL",
                  "every stuck point has a detecting question" if not und else f"undetectable: {und}"))
    off=spec.get("offer"); ms=spec.get("maturity_stages") or []
    if not off: R.append(("Commercial closure","N/A","—","no offer at this tier"))
    else:
        bounds=[b for s in ms for b in s.get("boundaries",[])]; cov=set(off.get("covers",[]))
        unc=[b for b in bounds if b not in cov]
        R.append(("Commercial closure","BLOCK","PASS" if not unc else "FAIL",
                  "every stage boundary maps to an offer" if not unc else f"uncovered boundaries: {unc}"))
    if not ms: R.append(("Two-faced coverage","N/A","—","no maturity stages"))
    else:
        miss=[s.get("id","?") for s in ms if not {"problem","mastery"}<=set(s.get("faces_covered",[]))]
        R.append(("Two-faced coverage","BLOCK","PASS" if not miss else "FAIL",
                  "both faces represented per stage" if not miss else f"missing a face: {miss}"))
    rk=spec.get("ranking")
    if not rk:
        R.append(("Ranking gap-derived","N/A","—","no ranking")); R.append(("Positional rationale","N/A","—","no ranking"))
    else:
        R.append(("Ranking gap-derived","BLOCK","PASS" if rk.get("derived_from")=="gap" else "FAIL",
                  "order = f(gap × reachability)" if rk.get("derived_from")=="gap" else f"order derived from '{rk.get('derived_from')}' — must be gap"))
        bad=[m.get("id","?") for m in rk.get("moves",[]) if (not m.get("rationale_key")) or m.get("rationale_key")=="generic" or str(m.get("rationale_key")).isdigit()]
        R.append(("Positional rationale","BLOCK","PASS" if not bad else "FAIL",
                  "every move keyed to a gap-pattern" if not bad else f"option-generic/score rationale: {bad}"))
    return R

def main():
    spec=json.load(open(sys.argv[1]))
    R=run(spec)
    print(f"\nGATE REPORT — {sys.argv[1].split('/')[-1]}  (tier {spec['tier']})")
    print("-"*78)
    for g,sev,st,d in R:
        mark={"PASS":"✓","FAIL":"✗","WARN":"!","—":"·"}[st]
        print(f" {mark} [{sev:<8}] {g:<28} {st:<5} {d}")
    blocked=[g for g,sev,st,_ in R if sev=="BLOCK" and st=="FAIL"]
    print("-"*78)
    if blocked:
        print(f" EMIT REFUSED — {len(blocked)} blocking gate(s) failed: {blocked}\n"); sys.exit(1)
    print(" EMIT OK — all blocking gates pass (advisories noted)\n"); sys.exit(0)

if __name__=="__main__": main()
