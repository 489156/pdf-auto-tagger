@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM PDF 자동 태깅 시스템 실행 스크립트
REM AI-Powered PDF Auto-Tagging System (APATS)

echo ================================================
echo  PDF 자동 태깅 시스템 (APATS)
echo  AI-Powered PDF Auto-Tagging System
echo ================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다.
    echo Python 3.10 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 가상환경 확인 및 생성
if not exist "venv" (
    echo [설정] 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo [오류] 가상환경 생성 실패
        pause
        exit /b 1
    )
)

REM 가상환경 활성화
echo [설정] 가상환경 활성화 중...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [오류] 가상환경 활성화 실패
    pause
    exit /b 1
)

REM 의존성 설치 확인
python -c "import PyMuPDF" >nul 2>&1
if errorlevel 1 (
    echo [설정] 필요한 패키지 설치 중... (처음 실행 시 시간이 걸릴 수 있습니다)
    pip install --upgrade pip setuptools wheel
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
)

REM 개발 모드 설치
pip install -e . >nul 2>&1

REM API 키 확인
if "%OPENAI_API_KEY%"=="" (
    echo [알림] OPENAI_API_KEY 환경변수가 설정되지 않았습니다.
    echo.
    set /p API_KEY="OpenAI API 키를 입력하세요 (또는 Enter로 환경변수 사용): "
    if not "!API_KEY!"=="" (
        set OPENAI_API_KEY=!API_KEY!
    ) else (
        echo [오류] API 키가 필요합니다.
        echo 환경변수를 설정하거나, run.bat를 수정하여 API 키를 입력해주세요.
        pause
        exit /b 1
    )
)

REM 입력 파일 확인
if "%1"=="" (
    echo.
    echo [사용법]
    echo   run.bat ^<입력PDF파일^> [출력PDF파일]
    echo.
    echo [예시]
    echo   run.bat input.pdf output.pdf
    echo   run.bat input.pdf
    echo.
    set /p INPUT_FILE="입력 PDF 파일 경로를 입력하세요: "
    if "!INPUT_FILE!"=="" (
        echo [오류] 입력 파일이 지정되지 않았습니다.
        pause
        exit /b 1
    )
) else (
    set INPUT_FILE=%1
)

REM 출력 파일 확인
if "%2"=="" (
    for %%F in ("%INPUT_FILE%") do set OUTPUT_FILE=%%~dpnF_tagged.pdf
    echo [알림] 출력 파일을 지정하지 않았습니다. 기본값 사용: %OUTPUT_FILE%
) else (
    set OUTPUT_FILE=%2
)

REM 파일/폴더 존재 확인
if exist "%INPUT_FILE%\NUL" (
    if "%2"=="" (
        set OUTPUT_FILE=outputs
        echo [알림] 출력 폴더를 지정하지 않았습니다. 기본값 사용: %OUTPUT_FILE%
    )
    if not exist "%OUTPUT_FILE%" (
        mkdir "%OUTPUT_FILE%"
    )
) else (
    if not exist "%INPUT_FILE%" (
        echo [오류] 입력 파일을 찾을 수 없습니다: %INPUT_FILE%
        pause
        exit /b 1
    )
)

echo.
echo ================================================
echo  처리 시작
echo ================================================
echo 입력 파일: %INPUT_FILE%
echo 출력 경로: %OUTPUT_FILE%
echo.

REM 실행
python -m src.main "%INPUT_FILE%" "%OUTPUT_FILE%"

if errorlevel 1 (
    echo.
    echo [오류] 처리 중 오류가 발생했습니다.
    pause
    exit /b 1
) else (
    echo.
    echo ================================================
    echo  처리 완료!
    echo ================================================
    echo 출력 파일: %OUTPUT_FILE%
    echo.
)

pause
