"""
PDF 파서 테스트
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.parser.pdf_parser import PDFParser, PDFError, EncryptedPDFError
from src.parser.content_extractor import ContentExtractor


class TestPDFParser:
    """PDFParser 클래스 테스트"""
    
    def test_init_file_not_found(self):
        """존재하지 않는 파일로 초기화 시 FileNotFoundError 발생"""
        with pytest.raises(FileNotFoundError):
            PDFParser("nonexistent.pdf")
    
    def test_init_invalid_file(self):
        """PDF가 아닌 파일로 초기화 시 ValueError 발생"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"Not a PDF")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError):
                PDFParser(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_context_manager(self):
        """Context manager 동작 테스트"""
        # 실제 PDF 파일이 없으면 스킵
        # TODO: 샘플 PDF 파일이 있을 때 실제 테스트 구현
        pass
    
    def test_get_page_count(self):
        """페이지 수 반환 테스트"""
        # 실제 PDF 파일이 없으면 스킵
        # TODO: 샘플 PDF 파일이 있을 때 실제 테스트 구현
        pass
    
    def test_extract_metadata(self):
        """메타데이터 추출 테스트"""
        # 실제 PDF 파일이 없으면 스킵
        # TODO: 샘플 PDF 파일이 있을 때 실제 테스트 구현
        pass
    
    def test_extract_text_blocks(self):
        """텍스트 블록 추출 테스트"""
        # 실제 PDF 파일이 없으면 스킵
        # TODO: 샘플 PDF 파일이 있을 때 실제 테스트 구현
        pass
    
    def test_extract_images(self):
        """이미지 추출 테스트"""
        # 실제 PDF 파일이 없으면 스킵
        # TODO: 샘플 PDF 파일이 있을 때 실제 테스트 구현
        pass
    
    def test_extract_tables(self):
        """표 추출 테스트"""
        # 실제 PDF 파일이 없으면 스킵
        # TODO: 샘플 PDF 파일이 있을 때 실제 테스트 구현
        pass
    
    def test_get_page_dimensions(self):
        """페이지 크기 반환 테스트"""
        # 실제 PDF 파일이 없으면 스킵
        # TODO: 샘플 PDF 파일이 있을 때 실제 테스트 구현
        pass


class TestContentExtractor:
    """ContentExtractor 클래스 테스트"""
    
    def test_filter_by_type(self):
        """타입별 필터링 테스트"""
        elements = [
            {"type": "text", "content": "Hello"},
            {"type": "image", "content": ""},
            {"type": "text", "content": "World"},
            {"type": "table", "content": "Data"}
        ]
        
        text_elements = ContentExtractor.filter_by_type(elements, "text")
        assert len(text_elements) == 2
        assert all(elem["type"] == "text" for elem in text_elements)
        
        image_elements = ContentExtractor.filter_by_type(elements, "image")
        assert len(image_elements) == 1
        assert image_elements[0]["type"] == "image"
    
    def test_filter_by_page(self):
        """페이지별 필터링 테스트"""
        elements = [
            {"page": 0, "content": "Page 0"},
            {"page": 1, "content": "Page 1"},
            {"page": 0, "content": "Page 0 again"},
            {"page": 2, "content": "Page 2"}
        ]
        
        page0_elements = ContentExtractor.filter_by_page(elements, 0)
        assert len(page0_elements) == 2
        assert all(elem["page"] == 0 for elem in page0_elements)
    
    def test_sort_by_position(self):
        """위치 순서 정렬 테스트"""
        elements = [
            {"page": 0, "bbox": [100, 200, 200, 250], "content": "Second"},
            {"page": 0, "bbox": [100, 100, 200, 150], "content": "First"},
            {"page": 1, "bbox": [100, 50, 200, 100], "content": "Third page"},
            {"page": 0, "bbox": [50, 150, 150, 200], "content": "Middle"}
        ]
        
        sorted_elements = ContentExtractor.sort_by_position(elements)
        
        # 페이지 0의 요소들이 Y 좌표 순으로 정렬되어야 함
        page0_sorted = [e for e in sorted_elements if e["page"] == 0]
        assert page0_sorted[0]["bbox"][1] <= page0_sorted[1]["bbox"][1]
        assert page0_sorted[1]["bbox"][1] <= page0_sorted[2]["bbox"][1]
        
        # 페이지 순서도 유지되어야 함
        assert sorted_elements[0]["page"] == 0
        assert sorted_elements[-1]["page"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
