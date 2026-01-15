"""
Output writer: generates structure XML, mapping JSON, and processing report.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Any
import json
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


@dataclass
class ProcessingReport:
    input_pdf: str
    output_pdf: str
    mapping_count: int
    errors: List[str]
    warnings: List[str]
    taxonomy_root: str = ""
    taxonomy_fingerprint: str = ""


class OutputWriter:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_structure_xml(self, elements: List[Dict[str, Any]], stem: str) -> Path:
        root = ET.Element("document")
        for elem in elements:
            node = ET.SubElement(root, elem.get("type", "element"))
            node.set("id", elem.get("element_id", ""))
            node.set("page", str(elem.get("page", 0)))
            bbox = elem.get("bbox", [0, 0, 0, 0])
            node.set("bbox", ",".join(str(b) for b in bbox))
            node.text = (elem.get("content") or "")[:500]

        tree = ET.ElementTree(root)
        path = self.output_dir / f"{stem}_structure.xml"
        tree.write(path, encoding="utf-8", xml_declaration=True)
        return path

    def write_mapping_json(self, mappings: List[Dict[str, Any]], stem: str) -> Path:
        path = self.output_dir / f"{stem}_mapping.json"
        path.write_text(json.dumps(mappings, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def archive_mapping(self, stem: str) -> None:
        current = self.output_dir / f"{stem}_mapping.json"
        previous = self.output_dir / f"{stem}_mapping.previous.json"
        if current.exists():
            previous.write_text(current.read_text(encoding="utf-8"), encoding="utf-8")

    def write_report(self, report: ProcessingReport, stem: str) -> Path:
        path = self.output_dir / f"{stem}_processing_report.json"
        path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def write_batch_report(self, results: List[Dict[str, Any]]) -> Path:
        path = self.output_dir / "batch_report.json"
        path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
