# 설치 가이드

## Windows 사용자

### 자동 설치 (권장)

1. **setup.bat** 더블클릭
2. 완료될 때까지 대기 (약 5-10분)
3. 완료!

### 수동 설치

명령 프롬프트(CMD)에서:

```batch
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
venv\Scripts\activate

# 3. pip 업그레이드
python -m pip install --upgrade pip

# 4. 패키지 설치
pip install -r requirements.txt

# 5. 개발 모드 설치
pip install -e .
```

---

## Linux/macOS 사용자

### 자동 설치

```bash
# 1. 실행 권한 부여
chmod +x setup.sh  # (있는 경우)

# 2. 실행
./setup.sh
```

### 수동 설치

```bash
# 1. 가상환경 생성
python3 -m venv venv

# 2. 가상환경 활성화
source venv/bin/activate

# 3. pip 업그레이드
python -m pip install --upgrade pip

# 4. 패키지 설치
pip install -r requirements.txt

# 5. 개발 모드 설치
pip install -e .
```

---

## 필수 요구사항

- **Python 3.10 이상**
- **인터넷 연결** (패키지 다운로드 및 API 통신)
- **OpenAI API 키** (사용 시 필요)

---

## 확인 방법

설치가 완료되었는지 확인:

```bash
# Windows
venv\Scripts\activate
python -m src.main --help

# Linux/macOS
source venv/bin/activate
python -m src.main --help
```

---

## 문제 해결

### Python을 찾을 수 없음

**해결**: Python 설치 시 "Add Python to PATH" 옵션을 체크했는지 확인

### 패키지 설치 실패

**해결**:
1. pip 업그레이드: `python -m pip install --upgrade pip`
2. 관리자 권한으로 실행 (Windows)
3. 인터넷 연결 확인

### 가상환경 오류

**해결**:
- Windows: `python -m venv venv` (venv 모듈 확인)
- Linux/macOS: `python3 -m venv venv`

---

## 다음 단계

설치가 완료되면:
1. [사용자_가이드.md](사용자_가이드.md) 참조
2. OpenAI API 키 준비
3. PDF 처리 시작!
