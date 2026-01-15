"""
태그 매칭 모듈

구조 분석 결과를 바탕으로 XML 태그를 매칭하는 모듈
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

from .alt_text_generator import AltTextGenerator

logger = logging.getLogger(__name__)


class TagMatcher:
    """
    구조 분석 결과를 XML 태그로 매칭하는 클래스
    
    규칙 기반과 AI 기반을 결합하여 태그를 매칭합니다.
    """
    
    # 매칭 규칙
    MATCHING_RULES = {
        "H1": {
            "font_size_min": 20,
            "bold": True,
            "position_y_max": 200,
            "unique": True
        },
        "H2": {
            "font_size_min": 16,
            "bold": True,
            "line_break_before": True
        },
        "H3": {
            "font_size_min": 14,
            "bold": True
        },
        "P": {
            "font_size_range": (10, 13),
            "bold": False,
            "min_words": 5
        },
        "Table": {
            "has_grid": True,
            "min_rows": 2,
            "min_cols": 2
        },
        "Figure": {
            "is_image": True,
            "has_caption": "optional"
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            config: 태그 매칭 규칙 설정
        """
        self.config = config or {}
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.enable_ai_matching = self.config.get("enable_ai_matching", True)
        self.enable_rule_matching = self.config.get("enable_rule_matching", True)
        self.enable_alt_text = self.config.get("enable_alt_text", True)
        self.alt_text_config = self.config.get("alt_text", {})
        self.alt_text_max_images = self.alt_text_config.get("max_images", 10)
    
    def match_tags(
        self,
        elements: List[Dict[str, Any]],
        structure: Dict[str, Any],
        api_key: Optional[str] = None,
        pdf_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        요소들에 XML 태그 매칭
        
        Args:
            elements: PDF 요소 리스트
            structure: StructureAnalyzer 결과
            
        Returns:
            {
                "tagged_elements": [
                    {
                        "id": str,
                        "tag": str,
                        "attributes": Dict,
                        "content": str,
                        "bbox": List[float],
                        "confidence": float
                    }
                ],
                "metadata": {
                    "title": str,
                    "language": str,
                    "tags_used": List[str]
                }
            }
        """
        logger.info(f"태그 매칭 시작: {len(elements)}개 요소")
        
        tagged_elements = []
        hierarchy = structure.get("hierarchy", {})
        reading_order = structure.get("reading_order", [])
        
        # 제목 추출 (메타데이터용)
        title = self._extract_title(elements, hierarchy)
        
        # Alt 텍스트 생성기 준비
        alt_text_generator = None
        if self.enable_alt_text and api_key:
            alt_text_generator = AltTextGenerator(
                api_key=api_key,
                model=self.alt_text_config.get("model", "gpt-4-vision-preview"),
                max_tokens=self.alt_text_config.get("max_tokens", 300),
                temperature=self.alt_text_config.get("temperature", 0.3),
                max_retries=self.alt_text_config.get("max_retries", 2),
                backoff_base=self.alt_text_config.get("backoff_base", 1.5)
            )

        alt_text_cache: Dict[str, str] = {}
        alt_text_count = 0

        # 요소별 태그 매칭
        for idx, elem in enumerate(elements):
            elem_id = elem.get("element_id", f"element_{idx}")
            
            # 구조 분석 결과에서 태그 가져오기
            if elem_id in hierarchy:
                suggested_tag = hierarchy[elem_id].get("tag", "P")
                level = hierarchy[elem_id].get("level", 0)
            else:
                suggested_tag = "P"
                level = 0
            
            # 규칙 기반 매칭
            rule_result = self._rule_based_matching(elem, suggested_tag)
            
            # AI 기반 매칭 (구조 분석 결과 활용)
            ai_result = (suggested_tag, 0.8) if self.enable_ai_matching else (suggested_tag, 0.5)
            
            # 결과 통합
            final_tag, confidence = self._merge_results(rule_result, ai_result)
            
            # 태그 속성 생성
            attributes = self._generate_attributes(final_tag, level, elem)

            # 이미지 요소의 Alt 텍스트 생성
            if elem.get("type") == "image" and alt_text_generator:
                cache_key = f"{elem.get('xref', '')}:{elem.get('image_index', '')}"
                if cache_key in alt_text_cache:
                    attributes["alt"] = alt_text_cache[cache_key]
                elif alt_text_count < self.alt_text_max_images:
                    alt_text = alt_text_generator.generate_alt_text(
                        image_element={**elem, "id": elem_id},
                        context=elements,
                        pdf_path=pdf_path,
                        metadata=metadata or {}
                    )
                    alt_text_cache[cache_key] = alt_text
                    attributes["alt"] = alt_text
                    alt_text_count += 1
            
            tagged_elements.append({
                "id": elem_id,
                "tag": final_tag,
                "attributes": attributes,
                "content": elem.get("content", ""),
                "bbox": elem.get("bbox", [0, 0, 0, 0]),
                "page": elem.get("page", 0),
                "confidence": confidence,
                "level": level
            })
        
        # 태그 검증 및 보정
        tagged_elements = self._validate_and_correct(tagged_elements)
        
        # 메타데이터 생성
        metadata = {
            "title": title,
            "language": "ko-KR",
            "tags_used": list(set(e["tag"] for e in tagged_elements))
        }
        
        logger.info(f"태그 매칭 완료: {len(tagged_elements)}개 요소 태그됨")
        
        return {
            "tagged_elements": tagged_elements,
            "metadata": metadata
        }
    
    def _rule_based_matching(self, element: Dict[str, Any], suggested_tag: str) -> Tuple[str, float]:
        """
        규칙 기반 태그 매칭
        
        Args:
            element: PDF 요소
            suggested_tag: 제안된 태그
            
        Returns:
            (tag, confidence) 튜플
        """
        if not self.enable_rule_matching:
            return (suggested_tag, 0.5)
        
        elem_type = element.get("type", "text")
        font_info = element.get("font_info", {})
        font_size = font_info.get("size", 11)
        flags = font_info.get("flags", 0)
        is_bold = bool(flags & 16)
        bbox = element.get("bbox", [0, 0, 0, 0])
        y_pos = bbox[1] if len(bbox) > 1 else 0
        content = element.get("content", "")
        
        # 타입별 기본 태그
        if elem_type == "image":
            return ("Figure", 0.9)
        elif elem_type == "table":
            table_data = element.get("data", [])
            if len(table_data) >= 2 and len(table_data[0]) >= 2:
                return ("Table", 0.9)
            else:
                return ("P", 0.6)
        
        # 텍스트 요소 규칙 적용
        score = 0.0
        matched_tag = suggested_tag
        
        # H1 규칙
        if font_size >= 20 and is_bold and y_pos < 200:
            score += 0.8
            if suggested_tag == "H1":
                matched_tag = "H1"
        
        # H2 규칙
        elif font_size >= 16 and is_bold:
            score += 0.7
            if suggested_tag in ["H2", "H1"]:
                matched_tag = "H2"
        
        # H3 규칙
        elif font_size >= 14 and is_bold:
            score += 0.6
            if suggested_tag in ["H3", "H2", "H1"]:
                matched_tag = "H3"
        
        # P 규칙
        elif 10 <= font_size <= 13 and not is_bold:
            word_count = len(content.split())
            if word_count >= 5:
                score += 0.7
                matched_tag = "P"
        
        confidence = min(score, 1.0) if score > 0 else 0.5
        
        return (matched_tag, confidence)
    
    def _merge_results(
        self,
        rule_result: Tuple[str, float],
        ai_result: Tuple[str, float]
    ) -> Tuple[str, float]:
        """
        규칙 기반 + AI 기반 결과 통합
        
        Args:
            rule_result: 규칙 기반 결과 (tag, confidence)
            ai_result: AI 기반 결과 (tag, confidence)
            
        Returns:
            (tag, confidence) 튜플
        """
        rule_tag, rule_conf = rule_result
        ai_tag, ai_conf = ai_result
        
        # 가중 평균
        weight_rule = 0.3
        weight_ai = 0.7
        
        # 태그가 같으면 신뢰도 증가
        if rule_tag == ai_tag:
            final_tag = rule_tag
            final_conf = min((rule_conf * weight_rule + ai_conf * weight_ai) * 1.2, 1.0)
        else:
            # AI 결과 우선
            final_tag = ai_tag
            final_conf = ai_conf * weight_ai + rule_conf * weight_rule
        
        return (final_tag, final_conf)
    
    def _generate_attributes(
        self,
        tag: str,
        level: int,
        element: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        태그 속성 생성
        
        Args:
            tag: 태그명
            level: 계층 레벨
            element: 원본 요소
            
        Returns:
            속성 딕셔너리
        """
        attributes = {}
        
        if tag.startswith("H"):
            attributes["level"] = level
            if tag == "H1":
                attributes["id"] = "title"
        
        if element.get("type") == "image":
            # 이미지의 경우 alt text는 별도 생성 필요
            attributes["alt"] = ""
        
        return attributes
    
    def _validate_and_correct(
        self,
        tagged_elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        태그 일관성 검증 및 자동 보정
        
        Args:
            tagged_elements: 태그된 요소 리스트
            
        Returns:
            보정된 요소 리스트
        """
        # H1이 없으면 첫 번째 H2를 H1으로 승격
        h1_count = sum(1 for e in tagged_elements if e["tag"] == "H1")
        if h1_count == 0:
            for elem in tagged_elements:
                if elem["tag"] == "H2":
                    elem["tag"] = "H1"
                    elem["level"] = 1
                    elem["attributes"]["id"] = "title"
                    break
        
        # H1이 여러 개면 첫 번째만 유지
        elif h1_count > 1:
            h1_found = False
            for elem in tagged_elements:
                if elem["tag"] == "H1":
                    if h1_found:
                        elem["tag"] = "H2"
                        elem["level"] = 2
                    else:
                        h1_found = True
        
        # 이미지에 alt text 없으면 기본값
        for elem in tagged_elements:
            if elem["tag"] == "Figure" and not elem["attributes"].get("alt"):
                elem["attributes"]["alt"] = "이미지"
        
        return tagged_elements
    
    def _extract_title(
        self,
        elements: List[Dict[str, Any]],
        hierarchy: Dict[str, Any]
    ) -> str:
        """
        문서 제목 추출
        
        Args:
            elements: PDF 요소 리스트
            hierarchy: 계층 구조
            
        Returns:
            제목 문자열
        """
        # H1 태그된 요소 찾기
        for idx, elem in enumerate(elements):
            elem_id = elem.get("element_id", f"element_{idx}")
            if elem_id in hierarchy:
                if hierarchy[elem_id].get("tag") == "H1":
                    return elem.get("content", "")[:200]  # 최대 200자
        
        # H1이 없으면 첫 번째 요소
        if elements:
            return elements[0].get("content", "")[:200]
        
        return ""
    
    
    def calculate_confidence(
        self,
        element: Dict[str, Any],
        matched_tag: str,
        rule_score: float,
        ai_score: float
    ) -> float:
        """
        신뢰도 계산
        
        Args:
            element: PDF 요소
            matched_tag: 매칭된 태그
            rule_score: 규칙 기반 점수
            ai_score: AI 기반 점수
            
        Returns:
            신뢰도 (0.0 - 1.0)
        """
        # 가중 평균
        weight_rule = 0.3
        weight_ai = 0.7
        
        base_confidence = rule_score * weight_rule + ai_score * weight_ai
        
        # 보정 요소
        font_info = element.get("font_info", {})
        font_size = font_info.get("size", 11)
        
        if font_size > 20:
            base_confidence *= 1.1
        
        if matched_tag == "H1":
            # H1은 특별 처리
            base_confidence *= 1.1
        
        return min(base_confidence, 1.0)
