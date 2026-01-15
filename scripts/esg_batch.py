#!/usr/bin/env python3
"""
ESG batch automation runner.

Flow:
1) optional taxonomy auto-update (download/unzip)
2) taxonomy validation
3) API key format check
4) PDF preflight checks
5) run batch processing
6) mapping diff report
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Any
import urllib.request
import zipfile

import yaml

from src.main import PDFAutoTagger
from src.output.mapping_diff import compute_mapping_diff
from src.output.summary_report import build_summary_report
from src.utils.preflight import (
    check_api_key_format,
    check_pdf_health,
    check_taxonomy_package,
    compute_taxonomy_fingerprint,
    verify_checksum
)

logger = logging.getLogger(__name__)


def download_taxonomy(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading taxonomy: %s", url)
    urllib.request.urlretrieve(url, dest)
    return dest


def unzip_taxonomy(zip_path: Path, extract_dir: Path) -> Path:
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
    return extract_dir


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def collect_pdfs(input_dir: Path) -> List[Path]:
    return sorted(input_dir.glob("*.pdf"))


def write_mapping_diff(output_dir: Path, stem: str, new_mapping_path: Path) -> Path | None:
    previous_mapping = output_dir / f"{stem}_mapping.previous.json"
    if not previous_mapping.exists():
        return
    old_data = json.loads(previous_mapping.read_text(encoding="utf-8"))
    new_data = json.loads(new_mapping_path.read_text(encoding="utf-8"))
    diff = compute_mapping_diff(old_data, new_data)
    diff_path = output_dir / f"{stem}_mapping.diff.json"
    diff_path.write_text(json.dumps(diff, ensure_ascii=False, indent=2), encoding="utf-8")
    return diff_path


def main() -> None:
    parser = argparse.ArgumentParser(description="ESG batch automation runner")
    parser.add_argument("input_dir", help="PDF input directory")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--config", required=True, help="Config YAML path")
    parser.add_argument("--api-key", required=True, help="OpenAI API key")
    args = parser.parse_args()

    config = load_config(args.config)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    taxonomy_cfg = config.get("taxonomy", {})
    taxonomy_root = taxonomy_cfg.get("root", "")
    taxonomy_url = taxonomy_cfg.get("url", "")
    taxonomy_auto = taxonomy_cfg.get("auto_update", False)
    taxonomy_checksum = taxonomy_cfg.get("checksum_sha256", "")
    taxonomy_backup = None
    previous_fingerprint = compute_taxonomy_fingerprint(taxonomy_root) if taxonomy_root else ""

    if taxonomy_auto and taxonomy_url:
        zip_path = output_dir / "taxonomy.zip"
        if taxonomy_root:
            taxonomy_backup = output_dir / "taxonomy_backup"
            if Path(taxonomy_root).exists():
                taxonomy_backup.mkdir(parents=True, exist_ok=True)
                for item in Path(taxonomy_root).rglob("*"):
                    dest = taxonomy_backup / item.relative_to(taxonomy_root)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if item.is_file():
                        dest.write_bytes(item.read_bytes())
        download_taxonomy(taxonomy_url, zip_path)
        if taxonomy_checksum and not verify_checksum(str(zip_path), taxonomy_checksum):
            raise RuntimeError("Taxonomy checksum mismatch.")
        taxonomy_root = str(unzip_taxonomy(zip_path, output_dir / "taxonomy"))
        config.setdefault("taxonomy", {})["root"] = taxonomy_root

    tax_result = check_taxonomy_package(taxonomy_root)
    if not tax_result["ok"]:
        if taxonomy_backup:
            logger.warning("Taxonomy validation failed, restoring backup.")
            config.setdefault("taxonomy", {})["root"] = str(taxonomy_backup)
            tax_result = check_taxonomy_package(str(taxonomy_backup))
        if not tax_result["ok"]:
            raise RuntimeError(f"Taxonomy validation failed: {tax_result['issues']}")

    if not check_api_key_format(args.api_key):
        raise RuntimeError("Invalid OpenAI API key format.")

    input_path = Path(args.input_dir)
    pdfs = collect_pdfs(input_path)
    preflight_issues = []
    for pdf in pdfs:
        result = check_pdf_health(str(pdf))
        if not result["ok"]:
            preflight_issues.append({"file": str(pdf), "issues": result["issues"]})
    if preflight_issues:
        raise RuntimeError(f"PDF preflight failed: {preflight_issues}")

    tagger = PDFAutoTagger(args.api_key, config)
    result = tagger.process_batch(str(input_path), str(output_dir))

    # mapping diff + metadata
    taxonomy_fingerprint = compute_taxonomy_fingerprint(config.get("taxonomy", {}).get("root", ""))
    metadata_path = output_dir / "taxonomy_version.json"
    metadata_path.write_text(
        json.dumps(
            {
                "taxonomy_root": config.get("taxonomy", {}).get("root", ""),
                "taxonomy_url": taxonomy_url,
                "checksum_sha256": taxonomy_checksum,
                "fingerprint": taxonomy_fingerprint
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )
    mapping_diffs = []
    for pdf in pdfs:
        stem = f"{pdf.stem}_tagged"
        mapping_path = output_dir / f"{stem}_mapping.json"
        if mapping_path.exists():
            diff_path = write_mapping_diff(output_dir, stem, mapping_path)
            if diff_path:
                mapping_diffs.append(
                    json.loads(diff_path.read_text(encoding="utf-8"))
                )

    summary = build_summary_report(
        taxonomy_changed=previous_fingerprint != taxonomy_fingerprint,
        taxonomy_fingerprint=taxonomy_fingerprint,
        mapping_diffs=mapping_diffs,
        preflight_issues=preflight_issues
    )
    summary_path = output_dir / "summary_report.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
