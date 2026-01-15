"""
Rule-based concept matcher for ESG taxonomy.
"""

from __future__ import annotations

from typing import Dict, List, Any
import logging
import re

from src.taxonomy.ifrs_taxonomy import IFRSTaxonomyManager

logger = logging.getLogger(__name__)


class ConceptMatcher:
    """
    Rule-based matcher: maps extracted PDF elements to taxonomy concept labels.
    """

    def __init__(self, taxonomy: IFRSTaxonomyManager):
        self.taxonomy = taxonomy

    def match(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        if not self.taxonomy.concepts:
            logger.warning("No taxonomy concepts loaded.")
            return results

        for elem in elements:
            if elem.get("type") not in {"text", "table"}:
                continue
            text = (elem.get("content") or "").strip()
            if not text:
                continue

            best = self._match_text(text)
            if not best:
                continue

            results.append({
                "element_id": elem.get("element_id"),
                "page": elem.get("page"),
                "bbox": elem.get("bbox"),
                "evidence_text": text[:200],
                "concept_id": best["concept_id"],
                "confidence": best["confidence"],
                "value": self._extract_value(text),
                "unit": self._extract_unit(text)
            })

        return results

    def _match_text(self, text: str) -> Dict[str, Any]:
        # naive matching against concept labels
        best_match = None
        for concept in self.taxonomy.concepts.values():
            if concept.label and concept.label.lower() in text.lower():
                best_match = {
                    "concept_id": concept.concept_id,
                    "confidence": 0.6
                }
                break
        return best_match or {}

    def _extract_value(self, text: str) -> str:
        match = re.search(r"([-+]?\d[\d,\.]*)", text)
        return match.group(1) if match else ""

    def _extract_unit(self, text: str) -> str:
        units = ["ton", "tCO2e", "kg", "kgCO2e", "MWh", "kWh", "USD", "KRW", "%"]
        for unit in units:
            if unit.lower() in text.lower():
                return unit
        return ""
