# BPFCo Link Repair Compiler

Report-only first.

Classifier adapted from:
Tomayachi/obsidian-vault-link-checker (MIT)

Matching order:
1. Normalized filename match
2. Frontmatter alias match
3. Levenshtein distance <= 2
4. Token-subset match
5. Otherwise classify as planned note

BPFCo remains authoritative:
- .vault-index.json
- vault-indexer.py
- existing note files

Safety:
- This compiler does NOT modify notes.
- It creates proposals only.
- Automatic repair will be enabled only for high-confidence proposals after review.
