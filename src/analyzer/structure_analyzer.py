"""
구조 분석 모듈

GPT-4를 활용하여 PDF 구조를 분석하는 클래스
"""

import logging
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
import time

logger = logging.getLogger(__name__)


class StructureAnalyzer:
    """
    GPT-4를 사용하여 PDF 구조를 분석하는 클래스
    
    PDF에서 추출한 요소들을 분석하여 문서 구조와 계층을 파악합니다.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.1,
        max_tokens: int = 4000
    ):
        """
        Args:
            api_key: OpenAI API 키
            model: 사용할 모델 (기본: gpt-4-turbo-preview)
            temperature: 모델 temperature (기본: 0.1)
            max_tokens: 최대 토큰 수 (기본: 4000)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def analyze_structure(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        PDF 요소들의 구조를 분석
        
        Args:
            elements: PDFParser에서 추출한 요소 리스트
            
        Returns:
            {
                "document_type": str,  # "report", "article", etc.
                "hierarchy": {
                    "element_id": {
                        "tag": str,  # "H1", "H2", "P", etc.
                        "level": int,
                        "parent": str,
                        "children": List[str]
                    }
                },
                "reading_order": List[str]  # element_id 순서
            }
        """
        logger.info(f"구조 분석 시작: {len(elements)}개 요소")
        
        try:
            # 프롬프트 생성
            prompt = self._create_analysis_prompt(elements)
            
            # GPT-4 호출
            response = self._call_gpt4(prompt)
            
            # 응답 파싱
            structure = self._parse_gpt_response(response, elements)
            
            logger.info(f"구조 분석 완료: 문서 유형={structure.get('document_type', 'unknown')}")
            return structure
            
        except Exception as e:
            logger.error(f"구조 분석 실패: {e}", exc_info=True)
            # Fallback: 규칙 기반 기본 구조 반환
            return self._fallback_structure(elements)
    
    def _create_analysis_prompt(self, elements: List[Dict[str, Any]]) -> str:
        """
        GPT-4용 프롬프트 생성
        
        Args:
            elements: PDF 요소 리스트
            
        Returns:
            프롬프트 문자열
        """
        # 시스템 프롬프트
        system_prompt = """당신은 문서 구조 분석 전문가입니다.
PDF에서 추출된 텍스트 블록들을 분석하여 적절한 HTML/XML 태그를 할당하는 것이 목표입니다.

태그 종류:
- H1: 문서 제목 (1개만)
- H2: 주요 섹션 제목
- H3-H6: 하위 제목
- P: 본문 단락
- Table: 표
- Figure: 이미지
- List: 목록

분석 시 고려사항:
1. 폰트 크기 (큰 텍스트 = 제목 가능성)
2. 굵기 (bold = 제목 가능성)
3. 위치 (상단 중앙 = 제목)
4. 문맥 (내용의 흐름)

JSON 형식으로만 응답하세요:
{
    "document_type": "문서 유형",
    "hierarchy": {
        "element_0": {
            "tag": "H1",
            "level": 1,
            "parent": null,
            "children": ["element_1", "element_2"]
        }
    },
    "reading_order": ["element_0", "element_1", ...]
}"""

        # 사용자 프롬프트: 요소 정보 구성
        elements_text = []
        for idx, elem in enumerate(elements[:50]):  # 최대 50개 요소로 제한
            elem_type = elem.get("type", "unknown")
            content = elem.get("content", "")[:200]  # 내용 길이 제한
            font_info = elem.get("font_info", {})
            font_size = font_info.get("size", 0)
            font_name = font_info.get("font", "")
            flags = font_info.get("flags", 0)
            is_bold = bool(flags & 16)  # PyMuPDF bold flag
            bbox = elem.get("bbox", [0, 0, 0, 0])
            page = elem.get("page", 0)
            element_id = elem.get("element_id", f"element_{idx}")
            
            elements_text.append(f"""Element {element_id}:
- Type: {elem_type}
- Text: {content}
- Font size: {font_size}pt
- Font: {font_name}
- Bold: {is_bold}
- Position: Page {page}, BBox ({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})""")
        
        user_prompt = "다음은 PDF에서 추출한 텍스트 블록입니다:\n\n" + "\n\n".join(elements_text) + "\n\n각 요소에 적절한 태그를 할당하고, 계층 구조를 JSON으로 반환하세요."
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _call_gpt4(self, prompt: str, max_retries: int = 3) -> str:
        """
        GPT-4 API 호출 (재시도 로직 포함)
        
        Args:
            prompt: 프롬프트
            max_retries: 최대 재시도 횟수
            
        Returns:
            응답 텍스트
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "당신은 문서 구조 분석 전문가입니다. JSON 형식으로만 응답하세요."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"}
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff
                    logger.warning(f"GPT-4 API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}. {wait_time}초 후 재시도...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"GPT-4 API 호출 최종 실패: {e}")
                    raise
    
    def _parse_gpt_response(self, response: str, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        GPT-4 응답 파싱
        
        Args:
            response: GPT-4 응답 텍스트
            elements: 원본 요소 리스트
            
        Returns:
            구조화된 딕셔너리
        """
        try:
            # JSON 파싱
            result = json.loads(response)
            
            # 기본 구조 보장
            if "document_type" not in result:
                result["document_type"] = "document"
            
            if "hierarchy" not in result:
                result["hierarchy"] = {}
            
            if "reading_order" not in result:
                result["reading_order"] = [
                    elements[i].get("element_id", f"element_{i}")
                    for i in range(min(len(elements), 50))
                ]
            
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"GPT-4 응답 JSON 파싱 실패: {e}. Fallback 구조 사용")
            return self._fallback_structure(elements)
    
    def _fallback_structure(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        규칙 기반 Fallback 구조 생성
        
        Args:
            elements: PDF 요소 리스트
            
        Returns:
            기본 구조 딕셔너리
        """
        hierarchy = {}
        reading_order = []
        
        h1_found = False
        
        for idx, elem in enumerate(elements):
            elem_id = elem.get("element_id", f"element_{idx}")
            reading_order.append(elem_id)
            
            elem_type = elem.get("type", "text")
            font_info = elem.get("font_info", {})
            font_size = font_info.get("size", 11)
            flags = font_info.get("flags", 0)
            is_bold = bool(flags & 16)
            bbox = elem.get("bbox", [0, 0, 0, 0])
            y_pos = bbox[1] if len(bbox) > 1 else 0
            
            # 태그 결정 (규칙 기반)
            if elem_type == "image":
                tag = "Figure"
                level = 0
            elif elem_type == "table":
                tag = "Table"
                level = 0
            elif not h1_found and font_size >= 20 and is_bold and y_pos < 200:
                tag = "H1"
                level = 1
                h1_found = True
            elif font_size >= 16 and is_bold:
                tag = "H2"
                level = 2
            elif font_size >= 14 and is_bold:
                tag = "H3"
                level = 3
            else:
                tag = "P"
                level = 0
            
            hierarchy[elem_id] = {
                "tag": tag,
                "level": level,
                "parent": None,
                "children": []
            }
        
        return {
            "document_type": "document",
            "hierarchy": hierarchy,
            "reading_order": reading_order
        }
