"""
Alt 텍스트 자동 생성 모듈

GPT-4 Vision을 활용한 이미지 대체 텍스트 생성
"""

import logging
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class AltTextGenerator:
    """
    이미지 대체 텍스트 자동 생성 클래스
    
    GPT-4 Vision API를 사용하여 WCAG 2.1 AA 기준에 맞는 Alt 텍스트를 생성합니다.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-vision-preview",
        max_tokens: int = 300,
        temperature: float = 0.3
    ):
        """
        Args:
            api_key: OpenAI API 키
            model: 사용할 Vision 모델 (기본: gpt-4-vision-preview)
            max_tokens: 최대 토큰 수 (기본: 300)
            temperature: 모델 temperature (기본: 0.3)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def generate_alt_text(
        self,
        image_element: Dict[str, Any],
        context: List[Dict[str, Any]],
        pdf_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        이미지 대체 텍스트 생성
        
        Args:
            image_element: 이미지 요소 (PDFParser에서 추출한 이미지 정보)
            context: 주변 문맥 요소들 (텍스트, 제목 등)
            pdf_path: PDF 파일 경로 (이미지 추출용)
            metadata: 문서 메타데이터 (제목, 언어 등)
            
        Returns:
            대체 텍스트 문자열 (20-200자)
        """
        logger.info(f"Alt 텍스트 생성 시작: 이미지 요소 {image_element.get('id', 'unknown')}")
        
        try:
            # 이미지 바이너리 추출
            image_base64 = self._extract_image_base64(image_element, pdf_path)
            if not image_base64:
                logger.warning("이미지 추출 실패, 기본값 사용")
                return self._generate_default_alt_text(image_element, context)
            
            # 주변 문맥 수집
            context_text = self._collect_context(context, image_element)
            
            # 메타데이터 준비
            title = metadata.get("title", "") if metadata else ""
            lang = metadata.get("language", "ko-KR") if metadata else "ko-KR"
            
            # 프롬프트 생성
            prompt = self._create_alt_text_prompt(title, lang, context_text)
            
            # GPT-4 Vision API 호출
            alt_text = self._call_vision_api(image_base64, prompt)
            
            # 후처리 및 검증
            alt_text = self._postprocess_alt_text(alt_text)
            
            logger.info(f"Alt 텍스트 생성 완료: {len(alt_text)}자")
            return alt_text
            
        except Exception as e:
            logger.error(f"Alt 텍스트 생성 실패: {e}", exc_info=True)
            # Fallback: 기본값 반환
            return self._generate_default_alt_text(image_element, context)
    
    def _extract_image_base64(
        self,
        image_element: Dict[str, Any],
        pdf_path: Optional[str] = None
    ) -> Optional[str]:
        """
        이미지를 Base64로 추출
        
        Args:
            image_element: 이미지 요소
            pdf_path: PDF 파일 경로
            
        Returns:
            Base64 인코딩된 이미지 문자열 (없으면 None)
        """
        if not pdf_path:
            return None
        
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            page_num = image_element.get("page", 0)
            
            if page_num >= len(doc):
                doc.close()
                return None
            
            page = doc[page_num]
            image_list = page.get_images()
            
            image_index = image_element.get("image_index", 0)
            if image_index >= len(image_list):
                doc.close()
                return None
            
            img = image_list[image_index]
            xref = img[0]
            
            # 이미지 데이터 추출
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            doc.close()
            
            # Base64 인코딩
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # MIME 타입 추가 (jpeg/png)
            image_ext = base_image.get("ext", "png")
            mime_type = f"image/{image_ext}"
            
            return f"data:{mime_type};base64,{image_base64}"
            
        except Exception as e:
            logger.warning(f"이미지 추출 실패: {e}")
            return None
    
    def _collect_context(
        self,
        context: List[Dict[str, Any]],
        image_element: Dict[str, Any]
    ) -> str:
        """
        주변 문맥 수집
        
        Args:
            context: 주변 요소 리스트
            image_element: 이미지 요소
            
        Returns:
            문맥 텍스트
        """
        if not context:
            return ""
        
        # 이미지 앞뒤 요소 추출 (최대 5개)
        image_page = image_element.get("page", 0)
        image_bbox = image_element.get("bbox", [0, 0, 0, 0])
        image_y = image_bbox[1] if len(image_bbox) > 1 else 0
        
        # 같은 페이지의 요소들 필터링
        same_page_elements = [
            elem for elem in context
            if elem.get("page") == image_page and elem.get("type") == "text"
        ]
        
        # Y 좌표 기준 정렬 (위에서 아래로)
        same_page_elements.sort(key=lambda x: x.get("bbox", [0, 0])[1] if len(x.get("bbox", [])) > 1 else 0)
        
        # 이미지 근처 요소 찾기 (위 2개, 아래 2개)
        context_texts = []
        for elem in same_page_elements:
            elem_y = elem.get("bbox", [0, 0])[1] if len(elem.get("bbox", [])) > 1 else 0
            content = elem.get("content", "").strip()
            
            if content:
                # 이미지 위 (Y 좌표가 작음)
                if elem_y < image_y:
                    context_texts.append(content)
                # 이미지 아래 (Y 좌표가 큼)
                elif elem_y > image_y and len([t for t in context_texts if t]) < 4:
                    context_texts.append(content)
        
        return "\n".join(context_texts[:5])  # 최대 5개
    
    def _create_alt_text_prompt(
        self,
        title: str,
        lang: str,
        context_text: str
    ) -> str:
        """
        Alt 텍스트 생성 프롬프트 생성
        
        Args:
            title: 문서 제목
            lang: 언어
            context_text: 주변 문맥 텍스트
            
        Returns:
            프롬프트 문자열
        """
        system_prompt = """당신은 접근성 전문가입니다. 주어진 이미지와 주변 문맥을 기반으로 
WCAG 2.1 AA 기준에 맞는 Alt 텍스트를 생성하세요.

출력 규칙:
- 길이: 20~200자
- 중복 표현 회피
- "이미지" 같은 일반어만 단독 사용 금지
- 이미지를 보지 못하는 사용자가 이해할 수 있도록 구체적으로 설명
- 차트/그래프인 경우: 유형, 데이터 포인트, 트렌드 설명
- 사진/일러스트인 경우: 주요 피사체, 배경, 색상, 의미 설명"""
        
        user_prompt = f"""다음 정보를 바탕으로 Alt 텍스트를 생성하세요.

[문서 메타데이터]
- 제목: {title}
- 언어: {lang}

[주변 문맥]
{context_text if context_text else "없음"}

[요청]
이미지를 보지 못하는 사용자가 이해할 수 있도록 1~2문장 Alt 텍스트를 작성하세요.
한국어로 작성하고, 20~200자로 제한하세요."""
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def _call_vision_api(
        self,
        image_base64: str,
        prompt: str
    ) -> str:
        """
        GPT-4 Vision API 호출
        
        Args:
            image_base64: Base64 인코딩된 이미지
            prompt: 프롬프트
            
        Returns:
            생성된 Alt 텍스트
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 접근성 전문가입니다. WCAG 2.1 AA 기준에 맞는 Alt 텍스트를 생성하세요."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_base64
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            alt_text = response.choices[0].message.content.strip()
            return alt_text
            
        except Exception as e:
            logger.error(f"GPT-4 Vision API 호출 실패: {e}")
            raise
    
    def _postprocess_alt_text(self, alt_text: str) -> str:
        """
        Alt 텍스트 후처리
        
        Args:
            alt_text: 원본 Alt 텍스트
            
        Returns:
            후처리된 Alt 텍스트
        """
        # 앞뒤 공백 제거
        alt_text = alt_text.strip()
        
        # 따옴표 제거
        alt_text = alt_text.strip('"\'')
        
        # 길이 검증 (20-200자)
        if len(alt_text) < 20:
            alt_text = alt_text + " (이미지)"
        elif len(alt_text) > 200:
            alt_text = alt_text[:197] + "..."
        
        # 일반어만 사용한 경우 보정
        if alt_text.lower() in ["이미지", "image", "그림", "사진", "picture"]:
            alt_text = "이미지 설명이 필요한 콘텐츠입니다."
        
        return alt_text
    
    def _generate_default_alt_text(
        self,
        image_element: Dict[str, Any],
        context: List[Dict[str, Any]]
    ) -> str:
        """
        기본 Alt 텍스트 생성 (Fallback)
        
        Args:
            image_element: 이미지 요소
            context: 주변 문맥
            
        Returns:
            기본 Alt 텍스트
        """
        # 주변 문맥에서 제목이나 설명 추출 시도
        for elem in context[:3]:  # 최대 3개 요소 확인
            content = elem.get("content", "").strip()
            if content and len(content) > 10:
                # 제목이나 설명 텍스트가 있으면 활용
                return f"{content[:50]} (관련 이미지)"
        
        # 기본값
        return "이미지"
