from pathlib import Path
import json
import re
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / ".vault-index.json"
OUT = ROOT / "Brain" / "Executive" / "LinkRepair" / "link_repair_report.json"

def normalize(s):
    return re.sub(r"""[\s\-_.,;:!?'"(){}\[\]#/\\]""", "", str(s)).lower()

def tokenize(s):
    return [x for x in re.split(r"[\s\-_]+", str(s)) if x]

def is_subset(a,b):
    return all(x in set(b) for x in a)

def levenshtein(a,b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    if len(a) > len(b):
        a,b = b,a

    row = list(range(len(a)+1))

    for j in range(1,len(b)+1):
        prev=row[0]
        row[0]=j

        for i in range(1,len(a)+1):
            val=min(
                row[i]+1,
                row[i-1]+1,
                prev+(a[i-1] != b[j-1])
            )
            prev=row[i]
            row[i]=val

    return row[len(a)]

def frontmatter_aliases(note):
    fm=note.get("frontmatter",{})
    if not isinstance(fm,dict):
        return []

    aliases=fm.get("aliases",[])
    if isinstance(aliases,str):
        aliases=[aliases]

    if not isinstance(aliases,list):
        return []

    return [str(x).strip() for x in aliases if str(x).strip()]

def build_index(notes):
    stems=[]
    norm={}

    for title,note in notes.items():
        path=str(note.get("path",f"{title}.md"))
        stem=Path(path).stem

        entry={
            "path":path,
            "stem":stem,
            "key":stem.lower(),
            "is_alias":False
        }

        stems.append(entry)

        k=normalize(stem)
        norm.setdefault(k,[]).append(entry)

        for alias in frontmatter_aliases(note):
            ae={
                "path":path,
                "stem":stem,
                "key":alias.lower(),
                "is_alias":True
            }

            norm.setdefault(normalize(alias),[]).append(ae)

    return stems,norm

def find_match(target,stems,norm):
    lower=str(target).lower()
    nt=normalize(lower)

    # 1. Exact normalized match.
    candidates=norm.get(nt,[])
    if candidates:
        chosen=next((x for x in candidates if not x["is_alias"]),candidates[0])
        return {
            "match":chosen["path"],
            "type":"alias match" if chosen["is_alias"] else "similar name",
            "confidence":"high"
        }

    # 2. Levenshtein <= 2.
    best=None
    bestdist=999

    for s in stems:
        if abs(len(s["key"])-len(lower))>2:
            continue

        d=levenshtein(lower,s["key"])

        if d<=2 and d<bestdist:
            bestdist=d
            best=s

    if best:
        return {
            "match":best["path"],
            "type":"possible match",
            "confidence":"medium",
            "distance":bestdist
        }

    # 3. Token subset.
    tt=tokenize(lower)

    if len(tt)>=2:
        for s in stems:
            st=tokenize(s["key"])
            if len(st)<2:
                continue

            if is_subset(tt,st) or is_subset(st,tt):
                return {
                    "match":s["path"],
                    "type":"possible match",
                    "confidence":"medium"
                }

    return None

def main():
    if not INDEX.exists():
        raise SystemExit("Missing .vault-index.json")

    data=json.loads(INDEX.read_text(encoding="utf-8-sig"))

    notes=data.get("notes",{})
    unresolved=data.get("unresolved_links",{})

    if not isinstance(notes,dict):
        notes={}

    if not isinstance(unresolved,dict):
        unresolved={}

    stems,norm=build_index(notes)

    rows=[]
    seen_targets=defaultdict(set)

    for source,targets in unresolved.items():
        if not isinstance(targets,list):
            continue

        for raw in targets:
            target=str(raw).strip()
            if not target:
                continue

            clean=target.split("|",1)[0]
            clean=clean.split("#",1)[0]
            clean=clean.replace("\\","/").strip()

            match=find_match(clean,stems,norm)

            row={
                "source":source,
                "target":target,
                "normalized_target":normalize(clean)
            }

            if match:
                row.update(match)
                seen_targets[normalize(clean)].add(source)
            else:
                row["type"]="planned note"
                row["confidence"]="none"
                seen_targets[normalize(clean)].add(source)

            rows.append(row)

    high=[x for x in rows if x["confidence"]=="high"]
    medium=[x for x in rows if x["confidence"]=="medium"]
    planned=[x for x in rows if x["confidence"]=="none"]

    recurring=[]
    for x in planned:
        if len(seen_targets.get(x["normalized_target"],set()))>1:
            recurring.append(x)

    report={
        "source":".vault-index.json",
        "compiler":"BPFCo Link Repair Compiler",
        "method":"Git-derived normalized + alias + Levenshtein<=2 + token-subset classifier",
        "scan_only":True,
        "totals":{
            "unresolved":len(rows),
            "high_confidence":len(high),
            "medium_confidence":len(medium),
            "planned":len(planned),
            "recurring_planned":len(recurring)
        },
        "proposals":{
            "high_confidence":high,
            "medium_confidence":medium,
            "planned":planned
        }
    }

    OUT.write_text(
        json.dumps(report,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    print("=== BPFCo LINK REPAIR COMPILER ===")
    print(f"Unresolved scanned : {len(rows)}")
    print(f"High confidence    : {len(high)}")
    print(f"Medium confidence  : {len(medium)}")
    print(f"Planned notes      : {len(planned)}")
    print(f"Recurring planned  : {len(recurring)}")
    print(f"Report             : {OUT}")
    print("")
    print("NO NOTES WERE MODIFIED.")

if __name__ == "__main__":
    main()

