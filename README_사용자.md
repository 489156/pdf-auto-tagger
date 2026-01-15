# PDF 자동 태깅 시스템 - 빠른 시작 가이드

> 일반 사용자를 위한 간단한 사용 가이드

## ⚡ 5분 안에 시작하기

### 1단계: Python 설치 (최초 1회만)

아직 Python이 없다면:
1. https://www.python.org/downloads/ 방문
2. Python 3.10 이상 다운로드 및 설치
3. 설치 시 **"Add Python to PATH"** 체크 ⭐ 중요!

### 2단계: OpenAI API 키 준비

1. https://platform.openai.com/api-keys 방문
2. 계정 생성 또는 로그인
3. API 키 생성 (`sk-...` 형태)

### 3단계: 프로그램 설정 (최초 1회만)

**setup.bat** 파일을 더블클릭하고 완료될 때까지 기다리세요.

> ⏱ 약 5-10분 소요 (인터넷 속도에 따라 다름)

### 4단계: PDF 처리

#### 방법 A: 대화형 실행 (가장 쉬움) ⭐

1. **run_interactive.bat** 더블클릭
2. API 키 입력
3. 입력 PDF 파일 경로 입력 (또는 드래그 & 드롭)
4. 출력 파일 이름 입력 (선택사항)
5. 완료!

#### 방법 B: 명령줄 실행

1. 명령 프롬프트 열기 (Win + R → `cmd` 입력)
2. 프로그램 폴더로 이동:
   ```
   cd C:\경로\pdf-auto-tagger
   ```
3. 실행:
   ```
   run.bat "입력파일.pdf" "출력파일.pdf"
   ```

#### 폴더 배치 처리 (선택)

```
run.bat "입력폴더" "출력폴더"
```
출력 폴더를 생략하면 `outputs` 폴더가 생성됩니다.

#### ESG 배치 자동화 (선택)

```
python scripts/esg_batch.py "입력폴더" "출력폴더" --config config/config.yaml --api-key "OPENAI_API_KEY"
```
taxonomy 업데이트 사용 시 `taxonomy.url`과 `taxonomy.checksum_sha256`를 함께 설정하면 무결성 검증과 버전 기록이 추가됩니다.
`summary_report.json`으로 taxonomy 변경 감지 및 매핑 diff 요약이 제공됩니다.

---

## 📋 파일 설명

| 파일 | 용도 |
|------|------|
| `setup.bat` | 초기 설정 (최초 1회만 실행) |
| `run_interactive.bat` | 대화형 실행 (추천) |
| `run.bat` | 명령줄 실행 |
| `setup.sh` | Linux/macOS 초기 설정 |
| `run.sh` | Linux/macOS 실행 |
| `사용자_가이드.md` | 상세 사용 설명서 |

---

## 🧭 배치 파일 실행 가이드 (핵심 요약)

### 1) 최초 1회 준비: setup.bat
1. `setup.bat`를 더블클릭
2. 가상환경/필수 패키지 설치 완료까지 대기
3. 완료 메시지 확인

### 2) 가장 쉬운 실행: run_interactive.bat
1. `run_interactive.bat` 더블클릭
2. OpenAI API 키 입력
3. 입력 PDF 경로 입력 (드래그 & 드롭 가능)
4. 출력 파일 경로 입력 (Enter 시 기본값)
5. 완료 메시지 확인

### 3) 명령줄 실행: run.bat
```bash
run.bat "입력파일.pdf" "출력파일.pdf"
```
출력 파일을 생략하면 자동으로 `_tagged.pdf`가 붙습니다.

---

## 💡 예시

### 예시 1: 보고서 PDF 처리

```
입력: report.pdf
출력: report_tagged.pdf (자동 생성)
```

### 예시 2: 여러 파일 처리

각 파일마다 `run.bat`를 실행하거나, 명령 프롬프트에서:

```bash
run.bat file1.pdf file1_tagged.pdf
run.bat file2.pdf file2_tagged.pdf
run.bat file3.pdf file3_tagged.pdf
```

---

## ❓ 자주 묻는 질문

**Q: 처음 실행하면 오래 걸리나요?**  
A: 네, `setup.bat`는 최초 1회만 실행하며 약 5-10분 걸립니다.

**Q: 매번 API 키를 입력해야 하나요?**  
A: 환경변수로 설정하면 입력하지 않아도 됩니다. ([사용자_가이드.md](사용자_가이드.md) 참조)

**Q: 어떤 PDF가 지원되나요?**  
A: 표준 PDF 형식이면 됩니다. 암호화된 PDF는 지원하지 않습니다.

**Q: 처리 시간이 얼마나 걸리나요?**  
A: PDF 크기에 따라 다릅니다:
- 1-5페이지: 약 1-2분
- 10-20페이지: 약 3-5분

**Q: 비용이 드나요?**  
A: OpenAI API 사용 비용이 발생합니다. PDF 1개당 약 $0.01-0.10 정도입니다.

---

## 🆘 문제가 생겼어요!

**Python 오류**
- Python이 설치되어 있는지 확인
- [Python 다운로드](https://www.python.org/downloads/)

**패키지 설치 오류**
- 인터넷 연결 확인
- 관리자 권한으로 실행

**API 키 오류**
- OpenAI API 키 확인
- 크레딧 잔액 확인

더 자세한 내용은 [사용자_가이드.md](사용자_가이드.md)를 참조하세요.

---

## 📞 지원

- GitHub Issues: 문제 신고
- 문서: [사용자_가이드.md](사용자_가이드.md)
- 개발자 문서: [README.md](README.md)

---

**즐거운 PDF 처리 되세요! 🎉**
