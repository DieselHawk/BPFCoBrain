# OmniRoute - File Ingestion & Multi-Model Orchestrator

## Overview

OmniRoute integrates file ingestion with intelligent multi-model token management:
- **Import files** from your computer into the brain
- **Track token usage** across all Claude models
- **Auto-fallback** when one model's tokens run out
- **Reset daily** token limits automatically

## Installation

OmniRoute requires the Anthropic SDK:
```bash
pip install anthropic
```

Set your API key:
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "your-api-key"
```

## Commands

### 1. Import Files

Import Python, JavaScript, Markdown, JSON, or other code files:

```bash
python omniroute.py import C:\path\to\file.py
```

Import multiple files:
```bash
python omniroute.py import C:\code\module.py C:\docs\notes.md C:\config.json --category 03-References
```

**Categories:**
- `03-References` (default) — External code/documentation
- `01-Concepts` — Conceptual files
- `02-Projects` — Project files
- `04-Fleeting-Notes` — Temporary files

**Supported types:**
- Code: `.py`, `.js`, `.ts`, `.java`, `.go`, `.cpp`, `.rust`
- Config: `.json`, `.yaml`, `.yml`
- Docs: `.md`, `.txt`

### 2. Check Token Status

See how many tokens you have left on each model:

```bash
python omniroute.py status
```

Output:
```
=== OmniRoute Token Status ===

claude-3-5-sonnet
  [██░░░░░░░░░░░░░░░░] 12% (24,000/200,000)
  Available: 176,000 tokens
```

### 3. Query with Auto-Fallback

Query the brain and automatically switch models if tokens run out:

```bash
python omniroute.py query "Explain my imported code"
```

With context:
```bash
python omniroute.py query "How does this work?" --context "See the imported module"
```

**Fallback order:**
1. `claude-3-5-sonnet` (usually fastest)
2. `claude-3-opus` (most capable)
3. `claude-3-haiku` (fastest for simple tasks)

If any model runs out, OmniRoute automatically tries the next one.

### 4. Reset Daily Limits

Reset token counters (typically done automatically at midnight):

```bash
python omniroute.py reset
```

## Workflow Example

```bash
# 1. Import your codebase
python omniroute.py import C:\myproject\src\*.py --category 02-Projects

# 2. Check tokens
python omniroute.py status

# 3. Query with brain context
python omniroute.py query "Refactor this function" --context "Using design patterns from my notes"

# OmniRoute will:
# - Query the vault for relevant notes
# - Combine with your context
# - Send to Claude
# - Auto-fallback if tokens run out
```

## How It Works

1. **File Import**
   - Scans file type
   - Creates markdown wrapper with metadata
   - Stores in vault with hash tracking (no duplicates)
   - Logs import in `.imports.json`

2. **Token Tracking**
   - Each model has a 200k token daily limit
   - Tracks usage in `~/.omniroute_usage.json`
   - Calculates available tokens per model

3. **Fallback Logic**
   - Checks available tokens for each model
   - If chosen model runs out, tries next
   - Maintains conversation continuity
   - Logs which model was used

## Integration with Brain

Once files are imported, they're part of your vault:
- Run `query-cli.py` to search them
- See them in Obsidian graph visualization
- Cross-reference with other notes using `[[links]]`
- Token counts remain independent

## Advanced: Custom Categories

To use a custom category:
```bash
python omniroute.py import file.py --category "my-custom-folder"
```

The folder will be created in your vault automatically.
