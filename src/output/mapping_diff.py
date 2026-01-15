"""
Compute mapping diff between two mapping.json files.
"""

from __future__ import annotations

from typing import Dict, List, Any


def _key(entry: Dict[str, Any]) -> str:
    return f"{entry.get('element_id')}::{entry.get('concept_id')}"


def compute_mapping_diff(old_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    old_map = {_key(item): item for item in old_data}
    new_map = {_key(item): item for item in new_data}

    added = [new_map[k] for k in new_map.keys() - old_map.keys()]
    removed = [old_map[k] for k in old_map.keys() - new_map.keys()]
    changed = []
    for key in new_map.keys() & old_map.keys():
        if new_map[key] != old_map[key]:
            changed.append({"before": old_map[key], "after": new_map[key]})

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed)
        }
    }
