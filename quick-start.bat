@echo off
REM Quick Start Script for WhatsApp Automation with uv (Windows)

echo 🚀 WhatsApp Automation Quick Start
echo ==================================

REM Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo 📦 Installing uv...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo ❌ Failed to install uv
        pause
        exit /b 1
    )
    echo ✅ uv installed successfully
    REM Refresh PATH for current session
    call refreshenv
) else (
    echo ✅ uv is already installed
)

REM Install dependencies
echo 📦 Installing dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check Tesseract
echo 🔍 Checking Tesseract OCR...
where tesseract >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Tesseract OCR not found!
    echo 📖 Please install Tesseract:
    echo    Download from: https://github.com/UB-Mannheim/tesseract/wiki
    echo    Add to PATH: C:\Program Files\Tesseract-OCR\
    echo.
    echo ⚠️  You can continue without Tesseract, but OCR won't work.
    set /p continue="Continue anyway? (y/N): "
    if /i not "%continue%"=="y" (
        exit /b 1
    )
) else (
    echo ✅ Tesseract OCR found
)

REM Run setup verification
echo 🧪 Running setup verification...
uv run python setup.py
if %errorlevel% neq 0 (
    echo ⚠️  Setup verification had issues
)

echo.
echo 🎉 Setup complete!
echo.
echo 🚀 To start the WhatsApp automation:
echo    uv run python main.py --interactive
echo.
echo 📖 For help:
echo    uv run python main.py --help
echo.
pause 