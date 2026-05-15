@echo off
chcp 65001 >nul
title Chess Game

echo ========================================
echo     Chess Game - Startup Script
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

:: Install backend dependencies
echo [1/4] Installing backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt >nul 2>&1

:: Start backend service
echo [2/4] Starting backend service (port 8000)...
start "ChessBackend" cmd /k "title ChessBackend && uvicorn main:app --reload --port 8000"

:: Wait for backend
echo       Waiting for backend...
timeout /t 5 /nobreak >nul

:: Start frontend HTTP server
echo [3/4] Starting frontend server (port 8080)...
cd /d "%~dp0frontend"
start "ChessFrontend" cmd /k "title ChessFrontend && python -m http.server 8080"

timeout /t 2 /nobreak >nul

:: Open browser
echo [4/4] Opening browser...
start http://localhost:8080/index.html

echo.
echo ========================================
echo     Startup Complete!
echo ========================================
echo.
echo   Frontend: http://localhost:8080
echo   Backend:  http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo   Close the command windows to stop services
echo ========================================
pause
