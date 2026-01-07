@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title CoinTracker - Stop Project
color 0C

echo.
echo ========================================
echo    CoinTracker - Stop Project
echo ========================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check project path
if not exist "docker-compose.yml" (
    echo Error: docker-compose.yml file not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check Docker installation
docker --version >nul 2>&1
if not errorlevel 1 (
    docker-compose --version >nul 2>&1
    if not errorlevel 1 (
        echo Stopping Docker containers...
        docker-compose down
        if not errorlevel 1 (
            echo [OK] Containers stopped successfully.
        ) else (
            echo [WARNING] Error stopping containers
        )
    )
) else (
    echo Docker is not installed - checking for local processes...
    echo.
    
    REM Stop processes on specific ports
    echo Stopping processes on ports 8000 and 6000...
    
    REM Find and kill process on port 8000 (Backend)
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
        echo Stopping process %%a on port 8000...
        taskkill /F /PID %%a >nul 2>&1
    )
    
    REM Find and kill process on port 6000 (Frontend)
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :6000 ^| findstr LISTENING') do (
        echo Stopping process %%a on port 6000...
        taskkill /F /PID %%a >nul 2>&1
    )
    
    REM Also try to kill Python and Node processes related to CoinTracker
    echo Stopping CoinTracker processes...
    taskkill /FI "WINDOWTITLE eq CoinTracker Backend*" /F >nul 2>&1
    taskkill /FI "WINDOWTITLE eq CoinTracker Frontend*" /F >nul 2>&1
    
    echo.
    echo [OK] Local processes stopped.
    echo Note: If processes are still running, please close Backend and Frontend windows manually.
)

echo.
echo ========================================
pause
