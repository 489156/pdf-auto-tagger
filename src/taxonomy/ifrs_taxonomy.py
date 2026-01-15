"""
IFRS/ISSB XBRL taxonomy loader (minimal).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TaxonomyConcept:
    concept_id: str
    label: str
    element_name: str
    element_type: str
    period_type: str
    balance: str
    references: List[str]


class IFRSTaxonomyManager:
    """
    Minimal taxonomy loader. Indexes concept elements and human-readable labels
    from IFRS/ISSB XBRL taxonomy packages.
    """

    def __init__(self, taxonomy_root: str):
        self.root = Path(taxonomy_root)
        self.concepts: Dict[str, TaxonomyConcept] = {}
        self.labels: Dict[str, str] = {}

    def load(self) -> None:
        if not self.root.exists():
            raise FileNotFoundError(f"Taxonomy root not found: {self.root}")

        xsd_files = list(self.root.rglob("*.xsd"))
        label_files = list(self.root.rglob("*lab*.xml"))

        self._load_xsd_concepts(xsd_files)
        self._load_labels(label_files)

        logger.info("Taxonomy loaded: %d concepts, %d labels", len(self.concepts), len(self.labels))

    def _load_xsd_concepts(self, xsd_files: Iterable[Path]) -> None:
        for xsd in xsd_files:
            try:
                tree = ET.parse(xsd)
                root = tree.getroot()
            except Exception as exc:
                logger.warning("Failed to parse XSD: %s (%s)", xsd, exc)
                continue

            ns = {
                "xsd": "http://www.w3.org/2001/XMLSchema",
            }
            for elem in root.findall(".//xsd:element", ns):
                name = elem.get("name")
                if not name:
                    continue
                concept_id = f"{xsd.stem}#{name}"
                concept = TaxonomyConcept(
                    concept_id=concept_id,
                    label=name,
                    element_name=name,
                    element_type=elem.get("type", ""),
                    period_type=elem.get("periodType", ""),
                    balance=elem.get("balance", ""),
                    references=[]
                )
                self.concepts[concept_id] = concept

    def _load_labels(self, label_files: Iterable[Path]) -> None:
        for lab in label_files:
            try:
                tree = ET.parse(lab)
                root = tree.getroot()
            except Exception as exc:
                logger.warning("Failed to parse label file: %s (%s)", lab, exc)
                continue

            for label in root.findall(".//{http://www.xbrl.org/2003/linkbase}label"):
                label_text = (label.text or "").strip()
                label_id = label.get("id", "")
                if label_id and label_text:
                    self.labels[label_id] = label_text

    def resolve_label(self, concept_id: str) -> Optional[str]:
        concept = self.concepts.get(concept_id)
        if concept:
            return concept.label
        return None
