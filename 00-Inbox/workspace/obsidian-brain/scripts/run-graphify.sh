#!/bin/bash
# Graphify Runner for Obsidian Brain
# Usage: ./run-graphify.sh [path] [options]

GRAPHIFY_VENV="C:/Users/Jaques/Documents/kimi/workspace/.graphify-venv/Scripts"
export PATH="$GRAPHIFY_VENV:$PATH"

if [ -z "$1" ]; then
    echo "Usage: ./run-graphify.sh [path] [options]"
    echo ""
    echo "Examples:"
    echo "  ./run-graphify.sh ./raw              # Extract knowledge graph from raw/"
    echo "  ./run-graphify.sh ./raw --obsidian   # Export to Obsidian vault"
    echo "  ./run-graphify.sh ./raw --code-only  # Code-only extraction (no LLM)"
    echo ""
    echo "For full options, run: graphify --help"
    exit 1
fi

graphify extract "$@"
