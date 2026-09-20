import json
from pathlib import Path

idx = json.loads(
    Path(".vault-index.json").read_text(encoding="utf-8-sig")
)

src = idx["notes"]["BRAIN-SETUP"]

print("SOURCE LINKS:", src["links"])

for target in src["links"]:
    t = (
        target.strip()
        .split("|", 1)[0]
        .split("#", 1)[0]
        .replace("\\", "/")
        .removesuffix(".md")
        .lstrip("./")
        .casefold()
    )

    print("\nTARGET:", target)
    print("NORMAL:", t)

    hits = []

    for key, note in idx["notes"].items():
        path = (
            str(note.get("path", ""))
            .replace("\\", "/")
            .removesuffix(".md")
            .casefold()
        )

        if (
            path == t
            or path.rsplit("/", 1)[-1] == t
            or str(key).casefold() == t
        ):
            hits.append(
                (key, note.get("path"), note.get("folder"))
            )

    print("CANDIDATES:", hits[:10])
