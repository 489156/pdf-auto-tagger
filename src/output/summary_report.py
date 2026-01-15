"""
Summary report builder for taxonomy updates and mapping diffs.
"""

from __future__ import annotations

from typing import Dict, List, Any


def build_summary_report(
    taxonomy_changed: bool,
    taxonomy_fingerprint: str,
    mapping_diffs: List[Dict[str, Any]],
    preflight_issues: List[Dict[str, Any]]
) -> Dict[str, Any]:
    total_added = sum(diff.get("counts", {}).get("added", 0) for diff in mapping_diffs)
    total_removed = sum(diff.get("counts", {}).get("removed", 0) for diff in mapping_diffs)
    total_changed = sum(diff.get("counts", {}).get("changed", 0) for diff in mapping_diffs)

    return {
        "taxonomy_changed": taxonomy_changed,
        "taxonomy_fingerprint": taxonomy_fingerprint,
        "diff_totals": {
            "added": total_added,
            "removed": total_removed,
            "changed": total_changed
        },
        "diff_files": len(mapping_diffs),
        "preflight_issues": preflight_issues
    }
