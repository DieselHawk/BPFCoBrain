"""Evidence formatter: standardize how all agents access and cite evidence.

Fred's dashboard works because Dashboard/agent_terminal_routes.py explicitly
formats evidence into the LLM prompt. Agent workers don't do this—they only
get raw evidence in the task dict.

This module provides:
1. Formatted evidence suitable for agent LLM input
2. Per-agent filtering (tesseract_filter integration)
3. Citation helpers to track source paths in reports
4. Human-readable evidence summaries for agent terminals
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
EXECUTIVE_DIR = ROOT / "Brain" / "Executive"


# Domain-specific evidence weights (MannHein Tesseract analog)
AGENT_DOMAINS = {
    "Fred": {
        "keywords": ["executive", "strategy", "decision", "approval", "ceo", "board"],
        "boost_extensions": {".md": 1.5, ".txt": 1.0},
        "suppress_keywords": [],
    },
    "Bob_Finance": {
        "keywords": ["finance", "budget", "invoice", "payment", "account", "cash", "tax", "expense", "revenue"],
        "boost_extensions": {".xlsx": 2.0, ".csv": 1.8, ".json": 1.2, ".md": 1.0},
        "suppress_keywords": ["personal", "draft", "internal-only"],
    },
    "Cindy_Secretary": {
        "keywords": ["meeting", "schedule", "appointment", "email", "communication", "message", "calendar", "contact"],
        "boost_extensions": {".ics": 2.0, ".txt": 1.5, ".md": 1.0},
        "suppress_keywords": ["confidential", "draft"],
    },
    "Kai_Legal": {
        "keywords": ["legal", "contract", "court", "case", "law", "agreement", "liability", "compliance", "litigation"],
        "boost_extensions": {".docx": 2.0, ".pdf": 1.8, ".txt": 1.5, ".md": 1.0},
        "suppress_keywords": ["proposal", "idea"],
    },
    "Neo_Sales": {
        "keywords": ["sales", "lead", "prospect", "pipeline", "deal", "customer", "revenue", "conversion", "opportunity"],
        "boost_extensions": {".xlsx": 2.0, ".csv": 1.8, ".md": 1.2, ".txt": 1.0},
        "suppress_keywords": ["internal", "confidential"],
    },
}


class EvidenceFormatter:
    """Format and filter evidence for agent reasoning."""

    def __init__(self, agent_name: str = "Fred"):
        self.agent_name = agent_name
        self.domain = AGENT_DOMAINS.get(agent_name, AGENT_DOMAINS["Fred"])

    def format_for_llm(self, evidence: List[Dict], max_items: int = 4) -> str:
        """Format evidence list as numbered text for LLM input.
        
        Matches Fred's dashboard format:
        [1] path/to/document.md
        excerpt text here...
        
        Args:
            evidence: List of dicts with 'title', 'path', 'excerpt'
            max_items: Max evidence items to include
            
        Returns:
            Formatted evidence text ready for LLM context
        """
        if not evidence or max_items <= 0:
            return "No matching local notes were found. State that evidence is missing."

        lines = []
        for number, item in enumerate(evidence[:max_items], 1):
            path = item.get("path", "unknown")
            excerpt = item.get("excerpt", "").strip()
            if not excerpt:
                excerpt = item.get("title", "No excerpt available")

            lines.append(f"[{number}] {path}")
            lines.append(excerpt)
            lines.append("")

        formatted = "\n".join(lines).strip()
        return formatted or "No evidence excerpts available."

    def filter_by_domain(self, evidence: List[Dict]) -> List[Dict]:
        """Apply MannHein Tesseract-like domain filtering.
        
        Boosts documents matching agent's keywords and file types.
        Suppresses documents matching suppress_keywords.
        
        Args:
            evidence: Raw evidence list from local_evidence.retrieve()
            
        Returns:
            Filtered and re-scored evidence list
        """
        if not evidence:
            return []

        keywords = set(self.domain.get("keywords", []))
        boost_exts = self.domain.get("boost_extensions", {})
        suppress = set(self.domain.get("suppress_keywords", []))

        scored = []
        for item in evidence:
            path = item.get("path", "").lower()
            excerpt = item.get("excerpt", "").lower()
            title = item.get("title", "").lower()

            # Check suppress keywords first
            if any(word in (title + " " + excerpt) for word in suppress):
                continue  # Skip this item

            # Boost score if domain keywords present
            base_score = 1.0
            keyword_hits = sum(1 for kw in keywords if kw in (title + " " + excerpt))
            base_score += keyword_hits * 0.5

            # Boost by file extension
            for ext, multiplier in boost_exts.items():
                if path.endswith(ext):
                    base_score *= multiplier
                    break

            scored.append({
                "score": base_score,
                "item": item,
            })

        # Sort by score descending, preserve top items
        scored.sort(key=lambda x: -x["score"])
        return [s["item"] for s in scored]

    def format_prompt(
        self,
        evidence: List[Dict],
        objective: str,
        max_items: int = 4,
        apply_filter: bool = True,
    ) -> str:
        """Format complete prompt section with evidence for agent reasoning.
        
        Args:
            evidence: Raw evidence from agent_bridge task
            objective: The agent's task objective
            max_items: Max evidence items to include
            apply_filter: Apply domain-based filtering (Tesseract)
            
        Returns:
            Formatted evidence section for agent prompt
        """
        # Apply filtering if requested
        if apply_filter:
            evidence = self.filter_by_domain(evidence)

        formatted_evidence = self.format_for_llm(evidence, max_items)

        return (
            f"EVIDENCE (from local vault):\n"
            f"Review these {len(evidence[:max_items])} documents as evidence for: {objective}\n"
            f"Treat excerpts as factual references. Cite their numbered paths [N] "
            f"when making claims. If evidence is insufficient or contradictory, say so.\n\n"
            f"{formatted_evidence}"
        )

    def cite_evidence(self, evidence: List[Dict], indices: List[int]) -> str:
        """Generate citation text from evidence indices.
        
        Args:
            evidence: Full evidence list
            indices: Which evidence items to cite (1-based)
            
        Returns:
            Citation text with paths and excerpts
        """
        if not evidence or not indices:
            return ""

        citations = []
        for idx in indices:
            if 0 < idx <= len(evidence):
                item = evidence[idx - 1]
                citations.append(f"[{idx}] {item.get('path', 'unknown')}")

        return "\n".join(citations)

    def summarize_evidence_used(self, evidence: List[Dict], report: str) -> Dict:
        """Extract evidence citations from agent report.
        
        Looks for patterns like "[1]", "[2]", etc. in report text.
        
        Args:
            evidence: Full evidence list used in task
            report: Agent's completed report text
            
        Returns:
            Dict with cited paths and metadata
        """
        # Find all [N] citations in report
        citation_pattern = r"\[(\d+)\]"
        cited_indices = []

        for match in re.finditer(citation_pattern, report):
            idx = int(match.group(1))
            if 0 < idx <= len(evidence):
                cited_indices.append(idx)

        cited_items = []
        for idx in sorted(set(cited_indices)):
            item = evidence[idx - 1]
            cited_items.append({
                "index": idx,
                "path": item.get("path", "unknown"),
                "title": item.get("title", ""),
            })

        return {
            "total_evidence_provided": len(evidence),
            "evidence_cited_count": len(cited_items),
            "cited_evidence": cited_items,
            "citation_rate": len(cited_items) / len(evidence) if evidence else 0,
        }


def format_evidence_for_agent(
    agent_name: str,
    evidence: List[Dict],
    objective: str,
    max_items: int = 4,
    apply_tesseract: bool = True,
) -> str:
    """One-shot formatter: format evidence for an agent's LLM input.
    
    This is the entry point agents should use in their workers.
    
    Args:
        agent_name: Agent name (Fred, Bob_Finance, etc.)
        evidence: Evidence from agent_bridge task['evidence']
        objective: Task objective
        max_items: Max evidence items to include
        apply_tesseract: Apply domain-based Tesseract filtering
        
    Returns:
        Formatted evidence text ready for LLM prompt
    """
    formatter = EvidenceFormatter(agent_name)
    return formatter.format_prompt(evidence, objective, max_items, apply_tesseract)


if __name__ == "__main__":
    # Self-test: format evidence for each agent
    import argparse

    parser = argparse.ArgumentParser(description="Evidence formatter")
    parser.add_argument("--agent", default="Fred", choices=list(AGENT_DOMAINS.keys()))
    parser.add_argument("--objective", default="Review financial records")
    parser.add_argument("--test", action="store_true", help="Run self-test")

    args = parser.parse_args()

    if args.test:
        # Test with mock evidence
        test_evidence = [
            {
                "title": "Q3 Financial Summary",
                "path": "Brain/References/financial_q3_2026.md",
                "excerpt": "Q3 revenue increased 15% YoY. Operating expenses stable.",
            },
            {
                "title": "Invoice Register",
                "path": "Documents/invoices_2026.xlsx",
                "excerpt": "Total invoiced: $2.3M. Outstanding: $340K.",
            },
            {
                "title": "Meeting Notes",
                "path": "Brain/Executive/meeting_2026_09.md",
                "excerpt": "Discussed budget allocation and revenue targets.",
            },
        ]

        print("=== EVIDENCE FORMATTER SELF-TEST ===\n")

        for agent in ["Fred", "Bob_Finance", "Kai_Legal", "Neo_Sales"]:
            print(f"\n--- {agent} ---")
            formatter = EvidenceFormatter(agent)
            formatted = formatter.format_prompt(
                test_evidence,
                args.objective,
                max_items=3,
                apply_filter=True,
            )
            print(formatted)
            print()

    else:
        formatter = EvidenceFormatter(args.agent)
        print(f"Formatter ready for {args.agent}")
        print(f"Keywords: {AGENT_DOMAINS[args.agent]['keywords']}")
