@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title CoinTracker Deployment
color 0A

echo.
echo ========================================
echo    CoinTracker - Deployment Script
echo ========================================
echo.

cd /d "%~dp0"

REM Check Docker
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker from https://www.docker.com/get-started
    pause
    exit /b 1
)
echo [OK] Docker is installed

REM Check Docker Compose
echo Checking Docker Compose...
set "COMPOSE_CMD="
docker-compose --version >nul 2>&1
if not errorlevel 1 (
    set "COMPOSE_CMD=docker-compose"
    echo [OK] Docker Compose found
) else (
    docker compose version >nul 2>&1
    if not errorlevel 1 (
        set "COMPOSE_CMD=docker compose"
        echo [OK] Docker Compose plugin found
    ) else (
        echo [ERROR] Docker Compose not found!
        pause
        exit /b 1
    )
)

REM Check docker-compose.yml
if not exist docker-compose.yml (
    echo [ERROR] docker-compose.yml not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Create settings.json if needed
if not exist settings.json (
    echo.
    echo [INFO] Creating settings.json...
    if exist settings.example.json (
        copy /Y settings.example.json settings.json >nul
    ) else (
        echo {> settings.json
        echo   "coingecko_api_key": "YOUR_API_KEY_HERE",>> settings.json
        echo   "default_top_coins": 100,>> settings.json
        echo   "default_weights": {>> settings.json
        echo     "price_change": 0.4,>> settings.json
        echo     "volume_change": 0.3,>> settings.json
        echo     "stability": 0.2,>> settings.json
        echo     "market_cap": 0.1>> settings.json
        echo   },>> settings.json
        echo   "default_data_history_days": 7,>> settings.json
        echo   "update_interval_seconds": 60>> settings.json
        echo }>> settings.json
    )
    echo [IMPORTANT] Please edit settings.json and add your API key!
    pause
)

REM Stop existing containers
echo.
echo Stopping existing containers...
if "%COMPOSE_CMD%"=="docker-compose" (
    docker-compose down >nul 2>&1
) else (
    docker compose down >nul 2>&1
)

REM Start containers
echo.
echo Building and starting containers...
echo This may take a few minutes...
echo.

if "%COMPOSE_CMD%"=="docker-compose" (
    docker-compose up -d --build
) else (
    docker compose up -d --build
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start containers!
    echo Check logs with: %COMPOSE_CMD% logs
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Project started successfully!
echo.
timeout /t 5 >nul

echo ========================================
echo    Application Access
echo ========================================
echo.
echo Frontend:    http://localhost
echo Backend API: http://localhost/api/
echo Admin Panel: http://localhost/admin/
echo.
echo ========================================
echo    Login Credentials
echo ========================================
echo.
echo Username: admin34_
echo Password: 123asd;p+_
echo.
echo ========================================
echo    Useful Commands
echo ========================================
echo.
echo View logs:    %COMPOSE_CMD% logs -f
echo Stop:         %COMPOSE_CMD% down
echo Restart:      %COMPOSE_CMD% restart
echo Status:       %COMPOSE_CMD% ps
echo.

echo Container status:
if "%COMPOSE_CMD%"=="docker-compose" (
    docker-compose ps
) else (
    docker compose ps
)

echo.
timeout /t 2 >nul
start http://localhost

echo.
pause
