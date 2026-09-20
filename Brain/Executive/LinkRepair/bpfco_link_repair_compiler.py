from pathlib import Path
import json
import re
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / ".vault-index.json"
OUT = ROOT / "Brain" / "Executive" / "LinkRepair" / "link_repair_report.json"

def clean_target(value):
    s = str(value or "").strip()

    # Obsidian-style target cleanup.
    if "|" in s:
        s = s.split("|", 1)[0]

    if "#" in s:
        s = s.split("#", 1)[0]

    s = s.replace("\\", "/").strip()

    # Remove leading ./ and trailing markdown extension.
    while s.startswith("./"):
        s = s[2:]

    if s.lower().endswith(".md"):
        s = s[:-3]

    return s.strip()

def normalize(value):
    s = clean_target(value).lower()
    return re.sub(r"[^a-z0-9]+", "", s)

def tokens(value):
    s = clean_target(value).lower()
    return re.findall(r"[a-z0-9]+", s)

def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    if len(a) > len(b):
        a, b = b, a

    prev = list(range(len(a) + 1))

    for j, cb in enumerate(b, 1):
        cur = [j]

        for i, ca in enumerate(a, 1):
            cur.append(min(
                cur[-1] + 1,
                prev[i] + 1,
                prev[i - 1] + (ca != cb)
            ))

        prev = cur

    return prev[-1]

def alias_list(note):
    fm = note.get("frontmatter", {})
    if not isinstance(fm, dict):
        return []

    aliases = fm.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]

    if not isinstance(aliases, list):
        return []

    return [str(x).strip() for x in aliases if str(x).strip()]

def add_identity(index, identity, entry):
    n = normalize(identity)
    if not n:
        return
    index.setdefault(n, []).append({
        **entry,
        "identity": identity
    })

def build_candidates(notes):
    exact = {}
    entries = []

    for note_key, note in notes.items():
        if not isinstance(note, dict):
            continue

        path = str(note.get("path", "")).strip()
        stem = Path(path).stem if path else str(note_key)
        folder = str(note.get("folder", "")).strip()
        title = str(note.get("title", "")).strip() or str(note_key)

        entry = {
            "note_key": str(note_key),
            "path": path,
            "folder": folder,
            "title": title
        }

        entries.append(entry)

        identities = {
            str(note_key),
            title,
            stem
        }

        if path:
            identities.add(path)
            identities.add(Path(path).name)
            identities.add(Path(path).stem)

        for alias in alias_list(note):
            identities.add(alias)

        for identity in identities:
            add_identity(exact, identity, entry)

    return entries, exact

def unique_entries(items):
    out = []
    seen = set()

    for x in items:
        k=(x["note_key"],x["path"])
        if k not in seen:
            seen.add(k)
            out.append(x)

    return out

def find_candidates(target, entries, exact):
    cleaned = clean_target(target)
    norm = normalize(cleaned)

    # 1. Exact normalized match across EVERY known BPFCo identity.
    exact_hits = unique_entries(exact.get(norm, []))

    if len(exact_hits) == 1:
        return {
            "type": "exact_match",
            "confidence": "high",
            "candidates": exact_hits,
            "matched_identity": exact.get(norm, [])[0].get("identity")
        }

    if len(exact_hits) > 1:
        return {
            "type": "ambiguous_exact_match",
            "confidence": "review",
            "candidates": exact_hits
        }

    # 2. Fuzzy normalized match.
    fuzzy = []

    for entry in entries:
        identities = [
            entry["note_key"],
            entry["title"],
            Path(entry["path"]).stem if entry["path"] else "",
            entry["path"]
        ]

        distances = [
            levenshtein(norm, normalize(x))
            for x in identities if normalize(x)
        ]

        if distances:
            d=min(distances)

            # Avoid ridiculous fuzzy matches.
            if d <= 2:
                fuzzy.append((d,entry))

    if fuzzy:
        fuzzy.sort(key=lambda x:(x[0],x[1]["path"]))

        best_distance=fuzzy[0][0]
        best=[
            x[1] for x in fuzzy
            if x[0]==best_distance
        ]

        best=unique_entries(best)

        if len(best)==1:
            return {
                "type":"near_match",
                "confidence":"medium",
                "distance":best_distance,
                "candidates":best
            }

        return {
            "type":"ambiguous_near_match",
            "confidence":"review",
            "distance":best_distance,
            "candidates":best
        }

    # 3. Token containment/subset match.
    target_tokens=set(tokens(cleaned))

    if target_tokens:
        token_hits=[]

        for entry in entries:
            candidate_strings=[
                entry["note_key"],
                entry["title"],
                Path(entry["path"]).stem if entry["path"] else ""
            ]

            candidate_token_sets=[
                set(tokens(x))
                for x in candidate_strings if tokens(x)
            ]

            for ct in candidate_token_sets:
                if target_tokens.issubset(ct) or ct.issubset(target_tokens):
                    token_hits.append(entry)
                    break

        token_hits=unique_entries(token_hits)

        if len(token_hits)==1:
            return {
                "type":"token_match",
                "confidence":"medium",
                "candidates":token_hits
            }

        if len(token_hits)>1:
            return {
                "type":"ambiguous_token_match",
                "confidence":"review",
                "candidates":token_hits
            }

    return {
        "type":"planned_note",
        "confidence":"none",
        "candidates":[]
    }

def main():
    if not INDEX.exists():
        raise SystemExit(f"Missing index: {INDEX}")

    data=json.loads(INDEX.read_text(encoding="utf-8-sig"))

    notes=data.get("notes",{})
    unresolved=data.get("unresolved_links",{})

    if not isinstance(notes,dict):
        notes={}

    if not isinstance(unresolved,dict):
        unresolved={}

    entries,exact=build_candidates(notes)

    rows=[]

    for source,targets in unresolved.items():
        targets=list(targets or [])

        for target in targets:
            result=find_candidates(target,entries,exact)

            row={
                "source":str(source),
                "target":str(target),
                "normalized_target":normalize(target),
                "type":result["type"],
                "confidence":result["confidence"]
            }

            if "distance" in result:
                row["distance"]=result["distance"]

            row["candidates"]=[
                {
                    "note_key":x["note_key"],
                    "path":x["path"],
                    "title":x["title"],
                    "folder":x["folder"]
                }
                for x in result["candidates"]
            ]

            if result.get("matched_identity"):
                row["matched_identity"]=result["matched_identity"]

            rows.append(row)

    high=[x for x in rows if x["confidence"]=="high"]
    medium=[x for x in rows if x["confidence"]=="medium"]
    review=[x for x in rows if x["confidence"]=="review"]
    planned=[x for x in rows if x["confidence"]=="none"]

    report={
        "compiler":"BPFCo Link Repair Compiler v2",
        "source":".vault-index.json",
        "scan_only":True,
        "schema":{
            "notes":"object keyed by note identity",
            "note_fields":["path","folder","word_count","links","frontmatter"],
            "unresolved_links":"source -> array of target strings"
        },
        "totals":{
            "unresolved":len(rows),
            "high_confidence":len(high),
            "medium_confidence":len(medium),
            "review":len(review),
            "planned":len(planned)
        },
        "proposals":{
            "high_confidence":high,
            "medium_confidence":medium,
            "review":review,
            "planned":planned
        }
    }

    OUT.write_text(
        json.dumps(report,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    print("=== BPFCo LINK REPAIR COMPILER v2 ===")
    print("Unresolved scanned :",len(rows))
    print("High confidence   :",len(high))
    print("Medium confidence :",len(medium))
    print("Needs review      :",len(review))
    print("Planned/missing   :",len(planned))
    print("Report            :",OUT)
    print("")
    print("NO NOTES WERE MODIFIED.")

if __name__=="__main__":
    main()
