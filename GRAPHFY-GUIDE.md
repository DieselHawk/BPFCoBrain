# Using Obsidian Graph Visualization

## Opening the Graph View

1. **Global Graph** (all connections)
   - Press `Ctrl+G` (or `Cmd+G` on Mac)
   - Shows entire vault connection lattice

2. **Local Graph** (current note only)
   - Bottom right panel → Graph icon
   - Shows connections for active note

## Graph Navigation

- **Click & drag** to pan
- **Scroll** to zoom in/out
- **Click a node** to view that note
- **Right-click node** for options

## Visualization Tips

- **Node size** = number of connections (bigger = more connected)
- **Links** = bidirectional connections between notes
- **Depth** = how many levels of connections to show (set to 3 in config)

## Optimizing Your Graph

To make the graph more useful:

1. **Use consistent link syntax:** `[[Note-Name]]`
2. **Create hub notes** (Maps of Content) to organize clusters
3. **Folder colors** appear automatically in the graph
4. **Remove .obsidian & Templates folders** from graph view if desired

## Graph Settings (in Obsidian)

Once Obsidian is open:
1. Settings → Core Plugins → Graph View (ensure enabled)
2. Open Graph → Settings icon (gear)
3. Adjust:
   - **Depth**: How many connection levels to show (1-3 recommended)
   - **Physics**: Toggle force-directed layout on/off
   - **Text fade**: How faded text appears at distance
   - **Link thickness**: Visual weight of connections

## Your Brain Architecture

Your vault is organized by folder for easy navigation:
- `00-Inbox` → Unprocessed ideas
- `01-Concepts` → Atomic ideas
- `05-Atomic` → Single-concept notes (best for dense graphs)
- `06-Maps-of-Content` → Hub nodes connecting related notes

The more you use bidirectional links (`[[like-this]]`), the richer your graph becomes!
