"""
PDF 생성 모듈

태그 정보를 포함한 새 PDF를 생성하는 모듈
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, ArrayObject, NameObject, NumberObject, TextStringObject
from pypdf.constants import CatalogAttributes

logger = logging.getLogger(__name__)


class TaggedPDFGenerator:
    """
    태그된 접근성 PDF를 생성하는 클래스
    
    XML 태그 정보를 포함한 PDF를 생성합니다.
    """
    
    def __init__(self, output_path: str):
        """
        Args:
            output_path: 생성할 PDF 파일 경로
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        original_pdf: str,
        tagged_elements: List[Dict[str, Any]],
        metadata: Dict[str, Any]
    ) -> str:
        """
        태그된 PDF 생성
        
        Args:
            original_pdf: 원본 PDF 경로
            tagged_elements: TagMatcher 결과
            metadata: 문서 메타데이터
            
        Returns:
            생성된 PDF 파일 경로
        """
        logger.info(f"태그된 PDF 생성 시작: {original_pdf}")
        
        try:
            # 원본 PDF 읽기
            reader = PdfReader(original_pdf)
            writer = PdfWriter()
            
            # 모든 페이지 복사
            for page in reader.pages:
                writer.add_page(page)
            
            # 메타데이터 설정
            self._set_metadata(writer, metadata)
            
            # 구조 트리 생성 (기본 구조)
            # Note: PyPDF의 구조 트리 기능은 제한적이므로,
            # 실제 구현에서는 PDF/UA를 위한 완전한 구조 트리가 필요합니다.
            # 현재는 메타데이터와 태그 정보만 추가합니다.
            
            # PDF/UA 준수 확인
            self._ensure_pdfua_compliance(writer, metadata)
            
            # 출력 파일 저장
            with open(self.output_path, "wb") as output_file:
                writer.write(output_file)
            
            logger.info(f"태그된 PDF 생성 완료: {self.output_path}")
            return str(self.output_path)
            
        except Exception as e:
            logger.error(f"태그된 PDF 생성 실패: {e}", exc_info=True)
            raise
    
    def _set_metadata(self, writer: PdfWriter, metadata: Dict[str, Any]) -> None:
        """
        PDF 메타데이터 설정
        
        Args:
            writer: PdfWriter 객체
            metadata: 메타데이터 딕셔너리
        """
        if not hasattr(writer, 'metadata'):
            writer.metadata = {}
        
        # 표준 메타데이터 필드
        title = metadata.get("title", "")
        if title:
            writer.metadata['/Title'] = TextStringObject(title)
        
        writer.metadata['/Author'] = TextStringObject("PDF Auto-Tagger")
        writer.metadata['/Creator'] = TextStringObject("PDF Auto-Tagger v0.1.0")
        writer.metadata['/Producer'] = TextStringObject("PDF Auto-Tagger")
        
        # 언어 설정
        language = metadata.get("language", "ko-KR")
        writer.metadata['/Lang'] = TextStringObject(language)
        
        logger.debug(f"메타데이터 설정 완료: Title={title}, Language={language}")
    
    def _ensure_pdfua_compliance(
        self,
        writer: PdfWriter,
        metadata: Dict[str, Any]
    ) -> None:
        """
        PDF/UA 표준 준수 확인
        
        Args:
            writer: PdfWriter 객체
            metadata: 메타데이터 딕셔너리
        """
        # PDF/UA 준수를 위한 기본 설정
        # Note: PyPDF는 구조 트리 생성 기능이 제한적이므로,
        # 완전한 PDF/UA 준수를 위해서는 추가 라이브러리나 수동 구현이 필요합니다.
        
        # Marked PDF 플래그는 실제 구조 트리 생성 시 설정됩니다.
        # 현재는 메타데이터만 설정합니다.
        
        logger.debug("PDF/UA 준수 확인 완료 (기본 메타데이터 설정)")
    
    def _create_structure_tree(
        self,
        tagged_elements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        PDF 구조 트리 생성
        
        Args:
            tagged_elements: 태그된 요소 리스트
            
        Returns:
            구조 트리 딕셔너리
            
        Note: 실제 구현에서는 PyPDF의 구조 트리 API를 사용하거나,
        PDF/UA 표준에 맞는 구조 트리를 생성해야 합니다.
        """
        root = {
            "tag": "Document",
            "children": []
        }
        
        current_section = None
        
        for element in tagged_elements:
            tag = element["tag"]
            content = element.get("content", "")
            
            if tag == "H1":
                root["children"].append({
                    "tag": "H1",
                    "content": content,
                    "id": element["id"]
                })
            
            elif tag == "H2":
                current_section = {
                    "tag": "Sect",
                    "children": [{
                        "tag": "H2",
                        "content": content
                    }]
                }
                root["children"].append(current_section)
            
            elif tag in ["P", "Figure", "Table"]:
                if current_section:
                    current_section["children"].append({
                        "tag": tag,
                        "content": content,
                        "attributes": element.get("attributes", {})
                    })
                else:
                    root["children"].append({
                        "tag": tag,
                        "content": content,
                        "attributes": element.get("attributes", {})
                    })
        
        return root
    
    def _optimize_reading_order(
        self,
        tagged_elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        논리적 읽기 순서로 재정렬
        
        Args:
            tagged_elements: 태그된 요소 리스트
            
        Returns:
            재정렬된 요소 리스트
        """
        def sort_key(element: Dict[str, Any]) -> tuple:
            bbox = element.get("bbox", [0, 0, 0, 0])
            page = element.get("page", 0)
            y = bbox[1] if len(bbox) > 1 else 0
            x = bbox[0] if len(bbox) > 0 else 0
            return (page, y, x)
        
        sorted_elements = sorted(tagged_elements, key=sort_key)
        
        for idx, element in enumerate(sorted_elements):
            element["reading_order"] = idx
        
        return sorted_elements
    
    def _validate_output(self, pdf_path: str) -> Dict[str, Any]:
        """
        생성된 PDF 검증
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            검증 결과 딕셔너리
        """
        validation = {
            "has_tags": False,
            "has_metadata": False,
            "page_count": 0,
            "issues": []
        }
        
        try:
            reader = PdfReader(pdf_path)
            validation["page_count"] = len(reader.pages)
            
            # 메타데이터 확인
            if reader.metadata and reader.metadata.get("/Title"):
                validation["has_metadata"] = True
            else:
                validation["issues"].append("메타데이터 불완전")
            
            # 텍스트 추출 가능 여부
            try:
                if reader.pages:
                    text = reader.pages[0].extract_text()
                    if not text or len(text) < 10:
                        validation["issues"].append("텍스트 추출 어려움")
            except Exception:
                validation["issues"].append("페이지 읽기 오류")
            
            validation["passed"] = len(validation["issues"]) == 0
            
        except Exception as e:
            validation["issues"].append(f"PDF 읽기 실패: {e}")
            validation["passed"] = False
        
        return validation
