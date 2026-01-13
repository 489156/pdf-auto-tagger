#!/usr/bin/env python3
"""
AI-Powered PDF Auto-Tagging System
메인 파이프라인
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Click을 사용한 CLI (선택적)
try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False

from src.parser.pdf_parser import PDFParser
from src.analyzer.structure_analyzer import StructureAnalyzer
from src.tagger.tag_matcher import TagMatcher
from src.generator.pdf_generator import TaggedPDFGenerator
from src.validator.accessibility_validator import AccessibilityValidator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFAutoTagger:
    """PDF 자동 태깅 파이프라인"""
    
    def __init__(
        self,
        openai_api_key: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            openai_api_key: OpenAI API 키
            config: 설정 딕셔너리
        """
        self.config = config or {}
        
        # 컴포넌트 초기화
        self.analyzer = StructureAnalyzer(
            api_key=openai_api_key,
            model=self.config.get("openai", {}).get("model", "gpt-4-turbo-preview"),
            temperature=self.config.get("openai", {}).get("temperature", 0.1),
            max_tokens=self.config.get("openai", {}).get("max_tokens", 4000)
        )
        self.tagger = TagMatcher(config=self.config.get("tagger", {}))
        self.validator = AccessibilityValidator(config=self.config.get("validator", {}))
    
    def process(
        self,
        input_pdf: str,
        output_pdf: str
    ) -> Dict[str, Any]:
        """
        PDF 자동 태깅 전체 프로세스
        
        Args:
            input_pdf: 입력 PDF 파일 경로
            output_pdf: 출력 PDF 파일 경로
            
        Returns:
            처리 결과 딕셔너리
        """
        logger.info(f"처리 시작: {input_pdf}")
        
        parser = None
        try:
            # 1. PDF 파싱
            logger.info("1/5 PDF 파싱 중...")
            parser = PDFParser(input_pdf)
            parsed_data = parser.parse()
            logger.info(f"   페이지: {parsed_data['pages']}개")
            logger.info(f"   요소: {len(parsed_data['elements'])}개")
            
            # 2. 구조 분석
            logger.info("2/5 AI 구조 분석 중...")
            structure = self.analyzer.analyze_structure(parsed_data['elements'])
            logger.info(f"   문서 유형: {structure.get('document_type', 'unknown')}")
            
            # 3. 태그 매칭
            logger.info("3/5 XML 태그 매칭 중...")
            tagged_result = self.tagger.match_tags(
                parsed_data['elements'],
                structure
            )
            
            # 신뢰도 통계
            confidences = [
                e.get('confidence', 0.5)
                for e in tagged_result['tagged_elements']
            ]
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
            else:
                avg_confidence = 0.5
            logger.info(f"   평균 신뢰도: {avg_confidence:.2%}")
            
            # 4. PDF 재생성
            logger.info("4/5 태그된 PDF 생성 중...")
            generator = TaggedPDFGenerator(output_pdf)
            output_path = generator.generate(
                input_pdf,
                tagged_result['tagged_elements'],
                tagged_result['metadata']
            )
            logger.info(f"   출력: {output_path}")
            
            # 5. 검증
            logger.info("5/5 접근성 검증 중...")
            validation_result = self.validator.validate(output_path)
            
            if validation_result['passed']:
                logger.info("   ✅ 모든 검증 통과")
            else:
                logger.warning(
                    f"   ⚠️ 경고 {len(validation_result['warnings'])}개, "
                    f"문제 {len(validation_result['issues'])}개"
                )
            
            # 결과 정리
            result = {
                "status": "success",
                "input_file": input_pdf,
                "output_file": output_path,
                "pages": parsed_data['pages'],
                "elements_processed": len(parsed_data['elements']),
                "average_confidence": avg_confidence,
                "validation": validation_result
            }
            
            logger.info("✨ 처리 완료!")
            return result
            
        except Exception as e:
            logger.error(f"❌ 오류 발생: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
        finally:
            if parser:
                parser.close()


def simple_main():
    """간단한 CLI 인터페이스 (Click 없이)"""
    if len(sys.argv) < 3:
        print("사용법: python -m src.main <input_pdf> <output_pdf>")
        print("환경변수 OPENAI_API_KEY를 설정하거나 --api-key 옵션을 사용하세요.")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    
    # API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("오류: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 처리
    tagger = PDFAutoTagger(api_key)
    result = tagger.process(input_pdf, output_pdf)
    
    # 결과 출력
    if result['status'] == 'success':
        print(f"\n✅ 성공!")
        print(f"입력: {result['input_file']}")
        print(f"출력: {result['output_file']}")
        print(f"페이지: {result['pages']}개")
    else:
        print(f"\n❌ 실패: {result.get('error', 'Unknown error')}")
        sys.exit(1)


# Click 명령 정의 (Click이 있는 경우)
if HAS_CLICK:
    @click.command()
    @click.argument('input_pdf', type=click.Path(exists=True))
    @click.argument('output_pdf', type=click.Path())
    @click.option(
        '--api-key',
        envvar='OPENAI_API_KEY',
        required=True,
        help='OpenAI API 키 (환경변수 OPENAI_API_KEY 사용 가능)'
    )
    @click.option(
        '--config',
        type=click.Path(exists=True),
        help='설정 파일 경로 (YAML)'
    )
    @click.option(
        '--verbose',
        is_flag=True,
        help='상세 로그 출력'
    )
    def main(input_pdf, output_pdf, api_key, config, verbose):
        """PDF 자동 태깅 도구"""
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 설정 로드
        config_dict = {}
        if config:
            try:
                import yaml
                with open(config, 'r', encoding='utf-8') as f:
                    config_dict = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패: {e}")
        
        # 처리
        tagger = PDFAutoTagger(api_key, config_dict)
        result = tagger.process(input_pdf, output_pdf)
        
        # 결과 출력
        if result['status'] == 'success':
            click.echo(f"\n✅ 성공!")
            click.echo(f"입력: {result['input_file']}")
            click.echo(f"출력: {result['output_file']}")
            click.echo(f"페이지: {result['pages']}개")
            click.echo(f"처리된 요소: {result['elements_processed']}개")
            click.echo(f"평균 신뢰도: {result['average_confidence']:.1%}")
            
            validation = result['validation']
            if validation['passed']:
                click.echo(f"\n접근성 검증: ✅ 통과 (점수: {validation['score']:.1f})")
            else:
                click.echo(f"\n접근성 검증: ⚠️ {len(validation['issues'])}개 문제")
                for issue in validation['issues']:
                    click.echo(f"  - {issue}")
        else:
            click.echo(f"\n❌ 실패: {result.get('error', 'Unknown error')}", err=True)
            sys.exit(1)
else:
    # Click이 없는 경우 simple_main을 main으로 사용
    def main():
        """CLI 진입점 (Click 없이)"""
        simple_main()


if __name__ == '__main__':
    if HAS_CLICK:
        main()
    else:
        simple_main()
