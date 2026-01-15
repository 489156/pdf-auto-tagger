@echo off
chcp 65001 >nul
REM PDF 자동 태깅 시스템 초기 설정 스크립트

echo ================================================
echo  PDF 자동 태깅 시스템 (APATS) 설정
echo ================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다.
    echo.
    echo Python 3.10 이상을 설치해주세요:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [확인] Python 설치 확인됨
python --version

echo.
echo [설정] 가상환경 생성 중...
if exist "venv" (
    echo [알림] 가상환경이 이미 존재합니다.
    choice /C YN /M "기존 가상환경을 삭제하고 다시 생성하시겠습니까"
    if errorlevel 2 goto skip_venv
    if errorlevel 1 (
        rmdir /s /q venv
    )
)

python -m venv venv
if errorlevel 1 (
    echo [오류] 가상환경 생성 실패
    pause
    exit /b 1
)
echo [완료] 가상환경 생성 완료

:skip_venv
echo.
echo [설정] 가상환경 활성화 중...
call venv\Scripts\activate.bat

echo.
echo [설정] pip 업그레이드 중...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [설정] 필요한 패키지 설치 중...
echo (시간이 걸릴 수 있습니다...)
pip install -r requirements.txt
if errorlevel 1 (
    echo [경고] 기본 설치 실패, 빌드 격리 없이 재시도합니다...
    pip install -r requirements.txt --no-build-isolation
    if errorlevel 1 (
        echo [오류] 패키지 설치 실패
        pause
        exit /b 1
    )
)

echo.
echo [설정] 개발 모드 설치 중...
pip install -e .

echo.
echo ================================================
echo  설정 완료!
echo ================================================
echo.
echo 다음 단계:
echo 1. OpenAI API 키를 준비하세요
echo 2. 환경변수 OPENAI_API_KEY를 설정하거나
echo    run.bat 실행 시 API 키를 입력하세요
echo 3. run.bat를 실행하여 PDF를 처리하세요
echo.
echo 예시:
echo   run.bat input.pdf output.pdf
echo.
pause
