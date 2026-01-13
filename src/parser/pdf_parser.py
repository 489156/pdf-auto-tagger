"""
PDF 파싱 모듈

PDF 파일을 파싱하고 구조 정보를 추출하는 클래스
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import fitz  # PyMuPDF
import pdfplumber

logger = logging.getLogger(__name__)


class PDFError(Exception):
    """PDF 처리 관련 오류"""
    pass


class EncryptedPDFError(PDFError):
    """암호화된 PDF 오류"""
    pass


class PDFParser:
    """
    PDF 파일을 파싱하고 구조 정보를 추출하는 클래스
    
    PyMuPDF (fitz)를 사용하여 PDF를 파싱하고,
    텍스트, 이미지, 표 등의 요소를 추출합니다.
    """
    
    def __init__(self, pdf_path: str):
        """
        Args:
            pdf_path: PDF 파일 경로
            
        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            PDFError: PDF가 손상되었거나 처리할 수 없는 경우
            EncryptedPDFError: PDF가 암호화된 경우
        """
        self.pdf_path = Path(pdf_path)
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        
        if not self.pdf_path.suffix.lower() == ".pdf":
            raise ValueError(f"PDF 파일이 아닙니다: {pdf_path}")
        
        self.doc: Optional[fitz.Document] = None
        self._open_pdf()
    
    def _open_pdf(self) -> None:
        """PDF 문서 열기"""
        try:
            self.doc = fitz.open(self.pdf_path)
            
            # 암호화 확인
            if self.doc.needs_pass:
                self.doc.close()
                raise EncryptedPDFError(
                    f"암호화된 PDF입니다. 비밀번호가 필요합니다: {self.pdf_path}"
                )
            
            logger.info(f"PDF 열기 성공: {self.pdf_path} (페이지 수: {len(self.doc)})")
            
        except fitz.FileDataError as e:
            raise PDFError(f"PDF 파일이 손상되었습니다: {self.pdf_path}") from e
        except Exception as e:
            raise PDFError(f"PDF 열기 실패: {self.pdf_path}") from e
    
    def __enter__(self):
        """Context manager 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()
    
    def close(self) -> None:
        """PDF 문서 닫기"""
        if self.doc:
            self.doc.close()
            self.doc = None
            logger.debug(f"PDF 닫기: {self.pdf_path}")
    
    def get_page_count(self) -> int:
        """
        페이지 수 반환
        
        Returns:
            PDF 페이지 수
        """
        if not self.doc:
            raise PDFError("PDF가 열려있지 않습니다")
        return len(self.doc)
    
    def parse(self) -> Dict[str, Any]:
        """
        PDF를 파싱하여 구조화된 정보 반환
        
        Returns:
            {
                "pages": int,
                "metadata": Dict,
                "elements": List[Dict]
            }
            
            elements의 각 항목:
            {
                "page": int,
                "type": str,  # "text", "image", "table"
                "bbox": List[float],  # [x0, y0, x1, y1]
                "content": str,
                "font_info": Dict
            }
        """
        if not self.doc:
            raise PDFError("PDF가 열려있지 않습니다")
        
        logger.info(f"PDF 파싱 시작: {self.pdf_path}")
        
        elements = []
        metadata = self._extract_metadata()
        
        for page_num in range(len(self.doc)):
            logger.debug(f"페이지 {page_num + 1}/{len(self.doc)} 처리 중...")
            
            # 텍스트 블록 추출
            text_blocks = self.extract_text_blocks(page_num)
            elements.extend(text_blocks)
            
            # 이미지 추출
            images = self.extract_images(page_num)
            elements.extend(images)
            
            # 표 추출 (pdfplumber 사용)
            tables = self.extract_tables(page_num)
            elements.extend(tables)
        
        result = {
            "pages": len(self.doc),
            "metadata": metadata,
            "elements": elements
        }
        
        logger.info(f"파싱 완료: {len(elements)}개 요소 추출")
        return result
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """
        PDF 메타데이터 추출
        
        Returns:
            메타데이터 딕셔너리
        """
        if not self.doc:
            return {}
        
        metadata = self.doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "pages": len(self.doc)
        }
    
    def extract_text_blocks(self, page_num: int) -> List[Dict[str, Any]]:
        """
        페이지에서 텍스트 블록 추출
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            
        Returns:
            텍스트 블록 리스트
            [
                {
                    "page": int,
                    "type": "text",
                    "bbox": [x0, y0, x1, y1],
                    "content": str,
                    "font_info": {
                        "font": str,
                        "size": float,
                        "flags": int,
                        "color": int
                    }
                }
            ]
        """
        if not self.doc or page_num >= len(self.doc):
            return []
        
        page = self.doc[page_num]
        blocks = []
        
        try:
            # get_text("dict")를 사용하여 구조화된 텍스트 추출
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" not in block:  # 이미지 블록 건너뛰기
                    continue
                
                block_text = []
                font_infos = []
                bbox_list = []
                
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            block_text.append(text)
                            
                            # 폰트 정보 수집
                            font_info = {
                                "font": span.get("font", ""),
                                "size": span.get("size", 0),
                                "flags": span.get("flags", 0),
                                "color": span.get("color", 0)
                            }
                            font_infos.append(font_info)
                            
                            # Bounding box
                            bbox_list.append(span.get("bbox", [0, 0, 0, 0]))
                
                if block_text:
                    # 블록 전체 bbox 계산
                    if bbox_list:
                        x0 = min(b[0] for b in bbox_list)
                        y0 = min(b[1] for b in bbox_list)
                        x1 = max(b[2] for b in bbox_list)
                        y1 = max(b[3] for b in bbox_list)
                        bbox = [x0, y0, x1, y1]
                    else:
                        bbox = block.get("bbox", [0, 0, 0, 0])
                    
                    # 대표 폰트 정보 (가장 큰 폰트 크기)
                    if font_infos:
                        main_font = max(font_infos, key=lambda f: f["size"])
                    else:
                        main_font = {}
                    
                    blocks.append({
                        "page": page_num,
                        "type": "text",
                        "bbox": bbox,
                        "content": " ".join(block_text),
                        "font_info": main_font
                    })
        
        except Exception as e:
            logger.warning(f"페이지 {page_num} 텍스트 추출 실패: {e}")
        
        return blocks
    
    def extract_images(self, page_num: int) -> List[Dict[str, Any]]:
        """
        페이지에서 이미지 추출
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            
        Returns:
            이미지 블록 리스트
            [
                {
                    "page": int,
                    "type": "image",
                    "bbox": [x0, y0, x1, y1],
                    "content": "",  # 이미지의 경우 빈 문자열
                    "image_index": int,
                    "width": float,
                    "height": float
                }
            ]
        """
        if not self.doc or page_num >= len(self.doc):
            return []
        
        page = self.doc[page_num]
        images = []
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # 이미지의 bbox 찾기
                image_rects = page.get_image_bbox(img)
                
                images.append({
                    "page": page_num,
                    "type": "image",
                    "bbox": list(image_rects),  # [x0, y0, x1, y1]
                    "content": "",  # 이미지는 텍스트 없음
                    "image_index": img_index,
                    "xref": img[0],  # 이미지 xref 번호
                    "width": image_rects.width,
                    "height": image_rects.height,
                    "font_info": {}  # 이미지는 폰트 정보 없음
                })
        
        except Exception as e:
            logger.warning(f"페이지 {page_num} 이미지 추출 실패: {e}")
        
        return images
    
    def extract_tables(self, page_num: int) -> List[Dict[str, Any]]:
        """
        페이지에서 표 추출 (pdfplumber 사용)
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            
        Returns:
            표 블록 리스트
            [
                {
                    "page": int,
                    "type": "table",
                    "bbox": [x0, y0, x1, y1],
                    "content": str,  # 표의 텍스트 표현
                    "data": List[List[str]],  # 표 데이터
                    "rows": int,
                    "cols": int
                }
            ]
        """
        if not self.doc:
            return []
        
        tables = []
        
        try:
            # pdfplumber를 사용하여 표 추출
            with pdfplumber.open(self.pdf_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    extracted_tables = page.extract_tables()
                    
                    for table in extracted_tables:
                        if not table:
                            continue
                        
                        # 표의 bbox 찾기
                        table_bbox = page.find_tables()[extracted_tables.index(table)].bbox
                        
                        # 표 데이터 정리
                        table_data = []
                        for row in table:
                            if row:
                                # None 값을 빈 문자열로 변환
                                cleaned_row = [str(cell) if cell is not None else "" for cell in row]
                                table_data.append(cleaned_row)
                        
                        if table_data:
                            # 표를 텍스트로 변환
                            table_text = "\n".join(["\t".join(row) for row in table_data])
                            
                            tables.append({
                                "page": page_num,
                                "type": "table",
                                "bbox": list(table_bbox),  # [x0, y0, x1, y1]
                                "content": table_text,
                                "data": table_data,
                                "rows": len(table_data),
                                "cols": len(table_data[0]) if table_data else 0,
                                "font_info": {}  # 표는 폰트 정보 별도 처리 필요
                            })
        
        except Exception as e:
            logger.warning(f"페이지 {page_num} 표 추출 실패: {e}")
        
        return tables
    
    def get_page_dimensions(self, page_num: int) -> Tuple[float, float]:
        """
        페이지 크기 반환
        
        Args:
            page_num: 페이지 번호 (0부터 시작)
            
        Returns:
            (width, height) 튜플
        """
        if not self.doc or page_num >= len(self.doc):
            raise ValueError(f"유효하지 않은 페이지 번호: {page_num}")
        
        page = self.doc[page_num]
        rect = page.rect
        return rect.width, rect.height
