@echo off
chcp 65001 >nul
title Chess Game

echo ========================================
echo     Chess Game - Quick Start
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

:: Start backend
echo [1/3] Starting backend (port 8000)...
cd /d "%~dp0backend"
start "ChessBackend" cmd /k "title ChessBackend && uvicorn main:app --reload --port 8000"

:: Wait for backend
echo       Waiting for backend...
timeout /t 3 /nobreak >nul

:: Open frontend HTML directly
echo [2/3] Opening frontend...
start "" "%~dp0frontend\index.html"

echo.
echo ========================================
echo     Started!
echo ========================================
echo.
echo   Backend: http://localhost:8000
echo   API:     http://localhost:8000/docs
echo.
echo   Close ChessBackend window to stop
echo ========================================
pause
