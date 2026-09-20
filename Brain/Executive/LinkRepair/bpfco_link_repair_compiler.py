from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / ".vault-index.json"
OUT = ROOT / "Brain" / "Executive" / "LinkRepair" / "link_repair_report.json"

def clean(value):
    s=str(value or "").strip()
    if "|" in s: s=s.split("|",1)[0]
    if "#" in s: s=s.split("#",1)[0]
    s=s.replace("\\","/").strip()
    while s.startswith("./"): s=s[2:]
    if s.lower().endswith(".md"): s=s[:-3]
    return s.strip()

def norm(value):
    return re.sub(r"[^a-z0-9]+","",clean(value).lower())

def toks(value):
    return re.findall(r"[a-z0-9]+",clean(value).lower())

def lev(a,b):
    if a==b:return 0
    if not a:return len(b)
    if not b:return len(a)
    if len(a)>len(b):a,b=b,a
    prev=list(range(len(a)+1))
    for j,cb in enumerate(b,1):
        cur=[j]
        for i,ca in enumerate(a,1):
            cur.append(min(
                cur[-1]+1,
                prev[i]+1,
                prev[i-1]+(ca!=cb)
            ))
        prev=cur
    return prev[-1]

def aliases(note):
    fm=note.get("frontmatter",{})
    if not isinstance(fm,dict):return []
    a=fm.get("aliases",[])
    if isinstance(a,str):a=[a]
    return [str(x) for x in a] if isinstance(a,list) else []

def entries(notes):
    out=[]
    exact={}

    for key,note in notes.items():
        if not isinstance(note,dict):continue

        path=str(note.get("path","")).strip()
        folder=str(note.get("folder","")).strip()
        title=str(note.get("title","")).strip() or str(key)
        stem=Path(path).stem if path else str(key)

        e={
            "note_key":str(key),
            "path":path,
            "folder":folder,
            "title":title,
            "stem":stem,
        }
        out.append(e)

        ids={str(key),title,stem}
        if path:
            ids.add(path)
            ids.add(Path(path).name)

        ids.update(aliases(note))

        for x in ids:
            n=norm(x)
            if n:
                exact.setdefault(n,[]).append(e)

    return out,exact

def uniq(xs):
    seen=set();out=[]
    for x in xs:
        k=(x["note_key"],x["path"])
        if k not in seen:
            seen.add(k);out.append(x)
    return out

def candidate_score(source,target,e):
    target_clean=clean(target)
    target_norm=norm(target_clean)
    score=0
    reasons=[]

    # Exact relative path.
    path=e["path"].replace("\\","/")
    if target_clean.lower()==path.lower():
        score+=100
        reasons.append("exact_path")

    # Exact filename/stem/title/key.
    ids=[e["note_key"],e["title"],e["stem"],e["path"],Path(path).name if path else ""]
    for x in ids:
        if target_norm and target_norm==norm(x):
            score=max(score,90)
            reasons.append("exact_identity")
            break

    # Source-folder context.
    source_folder=""
    if isinstance(source,dict):
        source_folder=str(source.get("folder",""))
    else:
        source_folder=str(source or "")

    if source_folder and e["folder"]:
        if norm(source_folder)==norm(e["folder"]):
            score+=18
            reasons.append("same_folder")

    # Folder embedded in target.
    target_clean_slash=target_clean.replace("\\","/")
    if "/" in target_clean_slash and path:
        if target_clean_slash.lower()==path.lower():
            score+=50
            reasons.append("path_match")

    # Small fuzzy distance.
    d=min(
        [lev(target_norm,norm(x)) for x in ids if norm(x)]
        or [999]
    )

    if d<=1:
        score+=35
        reasons.append("distance_1")
    elif d==2:
        score+=20
        reasons.append("distance_2")

    # Token relationship.
    tt=set(toks(target_clean))
    if tt:
        for x in [e["title"],e["stem"],e["note_key"]]:
            ct=set(toks(x))
            if tt and ct and (tt.issubset(ct) or ct.issubset(tt)):
                score+=12
                reasons.append("token_subset")
                break

    return score,reasons,d

def main():
    if not INDEX.exists():
        raise SystemExit(f"Missing {INDEX}")

    data=json.loads(INDEX.read_text(encoding="utf-8-sig"))
    notes=data.get("notes",{})
    unresolved=data.get("unresolved_links",{})

    if not isinstance(notes,dict):notes={}
    if not isinstance(unresolved,dict):unresolved={}

    all_entries,exact=entries(notes)
    rows=[]

    for source,targets in unresolved.items():
        # Resolve source metadata where possible.
        source_note=notes.get(source,{})
        if not isinstance(source_note,dict):source_note={}

        for target in list(targets or []):
            target_clean=clean(target)

            exact_hits=uniq(exact.get(norm(target_clean),[]))

            candidates=[]

            if exact_hits:
                for e in exact_hits:
                    score,reasons,d=candidate_score(source_note,target_clean,e)
                    candidates.append({
                        **e,
                        "score":score,
                        "reasons":reasons,
                        "distance":d
                    })
            else:
                for e in all_entries:
                    score,reasons,d=candidate_score(source_note,target_clean,e)
                    if score>=20:
                        candidates.append({
                            **e,
                            "score":score,
                            "reasons":reasons,
                            "distance":d
                        })

            candidates.sort(
                key=lambda x:(-x["score"],x["path"],x["note_key"])
            )

            if not candidates:
                confidence="none"
                kind="planned_note"
            else:
                top=candidates[0]
                second=candidates[1]["score"] if len(candidates)>1 else -1
                margin=top["score"]-second

                # High requires strong evidence and separation.
                if top["score"]>=100 and margin>=20:
                    confidence="high"
                    kind="strong_match"
                elif top["score"]>=70 and margin>=25:
                    confidence="high"
                    kind="context_match"
                elif top["score"]>=35 and margin>=15:
                    confidence="medium"
                    kind="near_match"
                elif top["score"]>=20:
                    confidence="review"
                    kind="ambiguous_candidate"
                else:
                    confidence="none"
                    kind="planned_note"

            rows.append({
                "source":str(source),
                "target":str(target),
                "type":kind,
                "confidence":confidence,
                "candidates":candidates[:5]
            })

    high=[x for x in rows if x["confidence"]=="high"]
    med=[x for x in rows if x["confidence"]=="medium"]
    review=[x for x in rows if x["confidence"]=="review"]
    planned=[x for x in rows if x["confidence"]=="none"]

    report={
        "compiler":"BPFCo Link Repair Compiler v2.1",
        "scan_only":True,
        "totals":{
            "unresolved":len(rows),
            "high_confidence":len(high),
            "medium_confidence":len(med),
            "review":len(review),
            "planned":len(planned)
        },
        "proposals":{
            "high_confidence":high,
            "medium_confidence":med,
            "review":review,
            "planned":planned
        }
    }

    OUT.write_text(
        json.dumps(report,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    print("=== BPFCo LINK REPAIR COMPILER v2.1 ===")
    print("Unresolved :",len(rows))
    print("High      :",len(high))
    print("Medium    :",len(med))
    print("Review    :",len(review))
    print("Planned   :",len(planned))
    print("Report    :",OUT)
    print("")
    print("NO NOTES WERE MODIFIED.")

if __name__=="__main__":
    main()
