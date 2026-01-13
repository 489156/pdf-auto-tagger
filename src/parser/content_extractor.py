"""
콘텐츠 추출 유틸리티 모듈

PDF에서 추출한 콘텐츠를 가공하는 유틸리티 함수들
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ContentExtractor:
    """콘텐츠 추출 및 가공 유틸리티 클래스"""
    
    @staticmethod
    def filter_by_type(elements: List[Dict[str, Any]], element_type: str) -> List[Dict[str, Any]]:
        """
        요소 리스트에서 특정 타입만 필터링
        
        Args:
            elements: 요소 리스트
            element_type: 필터링할 타입 ("text", "image", "table")
            
        Returns:
            필터링된 요소 리스트
        """
        return [elem for elem in elements if elem.get("type") == element_type]
    
    @staticmethod
    def filter_by_page(elements: List[Dict[str, Any]], page_num: int) -> List[Dict[str, Any]]:
        """
        요소 리스트에서 특정 페이지의 요소만 필터링
        
        Args:
            elements: 요소 리스트
            page_num: 페이지 번호
            
        Returns:
            필터링된 요소 리스트
        """
        return [elem for elem in elements if elem.get("page") == page_num]
    
    @staticmethod
    def sort_by_position(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        요소를 위치 순서로 정렬 (위에서 아래로, 왼쪽에서 오른쪽으로)
        
        Args:
            elements: 요소 리스트
            
        Returns:
            정렬된 요소 리스트
        """
        def sort_key(elem: Dict[str, Any]) -> tuple:
            bbox = elem.get("bbox", [0, 0, 0, 0])
            page = elem.get("page", 0)
            y = bbox[1] if len(bbox) > 1 else 0  # Y 좌표 (상단)
            x = bbox[0] if len(bbox) > 0 else 0  # X 좌표 (좌측)
            return (page, y, x)  # 페이지, Y, X 순으로 정렬
        
        return sorted(elements, key=sort_key)
