#!/usr/bin/env python3
"""Validate a Red Dot scoring spec: enumerate the reachable address space
(catch dead/unreachable cells) and run the exemplar test. Reference resolver is
the two-strand-quadrant pattern; generalize for richer schemas."""
import json, sys

def counts(n):
    d={0:1}
    for _ in range(n):
        nd={}
        for s,c in d.items():
            for f in range(1,6): nd[s+f]=nd.get(s+f,0)+c
        d=nd
    return d

def quad(s,t,thr):
    sH,tH=s>=thr,t>=thr
    return 'aligned' if(sH and tH)else 'lone' if(sH and not tH)else 'martyr' if(not sH and tH)else 'grinder'

def band(s,t,q,B):
    m=(s+t)/2; g=abs(s-t); c=B[q]
    return (c['high'] if m>=c['cut'] else c['low']) if c['measure']=='mean' else (c['high'] if g>=c['cut'] else c['low'])

def main():
    spec=json.load(open(sys.argv[1]))
    sN=spec['axes']['self']['items']; tN=spec['axes']['team']['items']
    thr=spec['scoring']['quadrant']['threshold']; B=spec['scoring']['bands']
    reach={}; total=0
    for ss,sc in counts(sN).items():
        for ts,tc in counts(tN).items():
            s,t=ss/sN,ts/tN; key=quad(s,t,thr)+'|'+band(s,t,quad(s,t,thr),B)
            reach[key]=reach.get(key,0)+sc*tc; total+=sc*tc
    print("REACHABLE ADDRESSES:")
    for k in sorted(reach): print(f"  {k:<24}{reach[k]/total*100:6.2f}% of answer space")
    rare=[k for k in reach if reach[k]/total<0.005]
    if rare: print("  WARN reachable-but-rare (under 0.5%):", rare)
    ex=spec.get('exemplars',[])
    LC=spec['scoring'].get('lifecycle')
    if ex:
        print("\nEXEMPLAR TEST:")
        ok=True
        def sidx(x):
            i=0
            for cut in (LC['cuts'] if LC else []):
                if x>=cut: i+=1
            return i
        for e in ex:
            q=quad(e['self'],e['team'],thr); good=(q==e['expect']); ok&=good
            extra=""
            if LC and 'journey' in e:
                ai=sidx((e['self']+e['team'])/2); ci=sidx(e['journey'])
                bb=spec['scoring'].get('normative',{}).get('behind_by',1)
                gs='behind' if (ci-ai)>=bb else ('ahead' if (ci-ai)<=-1 else 'on_track')
                extra=f"  | achieved={LC['stages'][ai]}, committed={LC['stages'][ci]} -> {gs}"
            print(f"  {'OK ' if good else 'XX '}{e['name']:<36} -> {q}{extra}")
        print("exemplar test:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
    else:
        print("\n(no exemplars in spec — add spec.exemplars to run the exemplar test)")

if __name__=='__main__': main()
