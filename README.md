# AI-Powered PDF Auto-Tagging System (APATS)

일반 PDF 문서를 입력받아 자동으로 구조적 XML 태그를 부여하고, WCAG 2.1 AA 준수 및 AI 친화적인 접근성 PDF로 변환하는 시스템

## 📋 프로젝트 개요

**APATS**는 AI 기반으로 PDF 문서에 자동으로 XML 태그를 부여하여 접근성을 향상시키는 도구입니다.

### 주요 기능

- 🤖 **PDF 구조 자동 인식**: 제목, 본문, 표, 이미지 자동 식별
- 🧠 **AI 기반 의미 분석**: GPT-4를 활용한 구조 분석
- 🏷️ **XML 태그 자동 매칭**: 적절한 태그 자동 할당
- 📝 **대체 텍스트 자동 생성**: 이미지 설명 자동 생성
- ✅ **접근성 검증**: WCAG 2.1 AA 준수 확인

## 🚀 빠른 시작

### Windows 사용자 (간단한 방법) ⭐

1. **setup.bat** 실행 (최초 1회만)
2. **run_interactive.bat** 실행
3. API 키 입력 및 PDF 파일 선택

> 📖 자세한 사용법: [사용자_가이드.md](사용자_가이드.md) 또는 [README_사용자.md](README_사용자.md)

### Linux/macOS 사용자

1. `chmod +x setup.sh run.sh`
2. `./setup.sh`
3. `./run.sh input.pdf output.pdf`

### 개발자용 설치

```bash
# 저장소 클론
git clone <repository-url>
cd pdf-auto-tagger

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 개발 모드 설치
pip install -e .
```

### 기본 사용

```python
from src.parser.pdf_parser import PDFParser

# PDF 파싱
parser = PDFParser("input.pdf")
result = parser.parse()

print(f"페이지 수: {result['pages']}")
print(f"요소 수: {len(result['elements'])}")
parser.close()
```

### Context Manager 사용

```python
with PDFParser("input.pdf") as parser:
    result = parser.parse()
    print(f"페이지 수: {result['pages']}")
```

### ESG Taxonomy 매핑 사용 (선택)

```bash
python -m src.main input.pdf output_tagged.pdf --config config/config.yaml
```

### 폴더 배치 처리 (선택)

```bash
python -m src.main /path/to/pdf_folder /path/to/output_dir
```

출력 경로를 생략하면 `outputs` 폴더가 생성됩니다.

### ESG 배치 자동화 실행 (taxonomy 업데이트/검증/차이 리포트)

```bash
python scripts/esg_batch.py /path/to/pdf_folder /path/to/output_dir --config config/config.yaml --api-key "$OPENAI_API_KEY"
```

taxonomy 업데이트를 사용할 경우 `taxonomy.url`과 `taxonomy.checksum_sha256`를 함께 설정하면
다운로드 무결성 검증과 버전 기록(`taxonomy_version.json`)이 생성됩니다.
또한 `summary_report.json`으로 taxonomy 변경 감지 및 매핑 diff 요약이 제공됩니다.

`config/config.yaml`의 `taxonomy.root`에 IFRS/ISSB taxonomy 패키지 경로를 지정하면
`{stem}_mapping.json`과 `{stem}_structure.xml` 및 `processing_report.json`이 함께 생성됩니다.

## 📁 프로젝트 구조

```
pdf-auto-tagger/
├── src/
│   ├── parser/           # PDF 파싱
│   │   ├── pdf_parser.py
│   │   └── content_extractor.py
│   ├── analyzer/         # AI 분석
│   ├── taxonomy/         # XBRL taxonomy 로딩
│   ├── matcher/          # Concept 매핑
│   ├── output/           # 결과 출력 (XML/JSON/리포트)
│   ├── tagger/          # 태그 매칭
│   ├── generator/       # PDF 재생성
│   └── validator/       # 검증
├── tests/               # 테스트
├── examples/            # 샘플 PDF
├── config/              # 설정 파일
├── requirements.txt
├── setup.py
└── README.md
```

## 🔧 기술 스택

- **Python 3.10+**
- **PyMuPDF**: PDF 파싱
- **pdfplumber**: 표 추출
- **OpenAI GPT-4**: 구조 분석
- **ReportLab**: PDF 생성

## 📝 개발 상태

현재 **Phase 1-4 + 고도화 작업 진행 중** 단계입니다.

- ✅ 프로젝트 구조 생성
- ✅ PDF 파서 구현
- ✅ AI 분석 엔진 구현
- ✅ 태그 매칭 로직 구현
- ✅ PDF 재생성 구현
- ✅ 접근성 검증 구현
- ✅ 메인 파이프라인 구현
- ✅ Alt 텍스트 자동 생성 모듈 구현 (v0.2.0)
- ✅ Alt 텍스트 자동 생성 파이프라인 통합 (v0.3.0)
- ⏳ 구조 트리(StructTreeRoot) 생성 고도화 (기본 구조 연결 완료)
- ⏳ 태그 매칭 정확도 개선 (진행 중)
- ⏳ 접근성 검증 고도화 (외부 도구 연동 옵션 추가)
- ⏳ E2E 테스트 체계 구축 (예정)

## 🧪 테스트

```bash
# 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest tests/ -v --cov=src
```

## 📄 라이선스

MIT License

## 🤝 기여

기여를 환영합니다! 이슈를 등록하거나 Pull Request를 보내주세요.

## 📧 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.
