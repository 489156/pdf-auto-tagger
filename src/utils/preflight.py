"""
Preflight validation utilities.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import hashlib
import re

import fitz


def check_api_key_format(api_key: str) -> bool:
    return bool(re.match(r"^sk-[A-Za-z0-9_-]{20,}$", api_key))


def check_pdf_health(pdf_path: str) -> Dict[str, Any]:
    result = {"ok": True, "issues": []}
    path = Path(pdf_path)
    if not path.exists():
        result["ok"] = False
        result["issues"].append("파일이 존재하지 않음")
        return result
    if path.suffix.lower() != ".pdf":
        result["ok"] = False
        result["issues"].append("PDF 확장자가 아님")
        return result

    try:
        doc = fitz.open(str(path))
        if doc.needs_pass:
            result["ok"] = False
            result["issues"].append("암호화된 PDF")
        if len(doc) == 0:
            result["ok"] = False
            result["issues"].append("페이지 수가 0")
        doc.close()
    except Exception:
        result["ok"] = False
        result["issues"].append("PDF 열기 실패")
    return result


def check_taxonomy_package(root: str) -> Dict[str, Any]:
    result = {"ok": True, "issues": []}
    path = Path(root)
    if not root:
        result["ok"] = False
        result["issues"].append("taxonomy.root 미설정")
        return result
    if not path.exists():
        result["ok"] = False
        result["issues"].append("taxonomy 경로 없음")
        return result
    xsd_files = list(path.rglob("*.xsd"))
    if not xsd_files:
        result["ok"] = False
        result["issues"].append("taxonomy XSD 파일 없음")
    return result


def compute_taxonomy_fingerprint(root: str) -> str:
    path = Path(root)
    if not path.exists():
        return ""
    files = sorted(path.rglob("*.xsd")) + sorted(path.rglob("*lab*.xml"))
    hasher = hashlib.sha256()
    for file_path in files:
        hasher.update(str(file_path).encode("utf-8"))
        try:
            hasher.update(file_path.read_bytes())
        except Exception:
            continue
    return hasher.hexdigest()


def verify_checksum(file_path: str, expected_sha256: str) -> bool:
    if not expected_sha256:
        return True
    hasher = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest() == expected_sha256
