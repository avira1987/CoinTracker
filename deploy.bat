@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title CoinTracker - Single File Deployment
color 0A

echo.
echo ========================================
echo    CoinTracker - Deployment Script
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM بررسی نصب Docker
echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker from https://www.docker.com/get-started
    pause
    exit /b 1
)

echo [OK] Docker is installed

REM بررسی نصب Docker Compose
echo Checking Docker Compose installation...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose is not installed!
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

echo [OK] Docker Compose is available

REM بررسی docker-compose.yml
if not exist "docker-compose.yml" (
    echo [ERROR] docker-compose.yml not found!
    echo Please make sure you're in the project root directory
    pause
    exit /b 1
)

REM ایجاد settings.json در صورت عدم وجود
if not exist "settings.json" (
    echo.
    echo [INFO] settings.json not found
    echo Creating settings.json from settings.example.json...
    
    if exist "settings.example.json" (
        copy /Y settings.example.json settings.json >nul
        echo [OK] settings.json created
        echo.
        echo [IMPORTANT] Please edit settings.json and add your CoinGecko API key!
        echo You can get a free API key from: https://www.coingecko.com/api
        echo.
        pause
    ) else (
        echo [WARNING] settings.example.json not found, creating default settings.json
        (
            echo {
            echo   "coingecko_api_key": "YOUR_API_KEY_HERE",
            echo   "default_top_coins": 100,
            echo   "default_weights": {
            echo     "price_change": 0.4,
            echo     "volume_change": 0.3,
            echo     "stability": 0.2,
            echo     "market_cap": 0.1
            echo   },
            echo   "default_data_history_days": 7,
            echo   "update_interval_seconds": 60
            echo }
        ) > settings.json
        echo [IMPORTANT] Please edit settings.json and add your CoinGecko API key!
        pause
    )
) else (
    echo [OK] settings.json exists
)

REM توقف کانتینرهای قبلی
echo.
echo Stopping any existing containers...
%COMPOSE_CMD% down >nul 2>&1

REM Build و اجرای کانتینرها
echo.
echo Building and starting Docker containers...
echo This may take a few minutes on first run...
echo.

%COMPOSE_CMD% up -d --build

if not errorlevel 1 (
    echo.
    echo [SUCCESS] Project started successfully!
    echo.
    echo Waiting for services to be ready...
    ping 127.0.0.1 -n 6 >nul
    
    echo.
    echo ========================================
    echo    Application Access
    echo ========================================
    echo.
    echo Frontend:    http://localhost
    echo Backend API: http://localhost/api/
    echo Admin Panel: http://localhost/admin/
    echo.
    echo ========================================
    echo    Default Login Credentials
    echo ========================================
    echo.
    echo Username: admin34_
    echo Password: 123asd;p+_
    echo.
    echo [SECURITY] Please change the default password in production!
    echo.
    echo ========================================
    echo    Useful Commands
    echo ========================================
    echo.
    echo View logs:        %COMPOSE_CMD% logs -f
    echo Stop services:    %COMPOSE_CMD% down
    echo Restart services: %COMPOSE_CMD% restart
    echo View status:      %COMPOSE_CMD% ps
    echo.
    
    REM بررسی وضعیت کانتینرها
    echo Container status:
    %COMPOSE_CMD% ps
    echo.
    
    echo Opening browser at http://localhost...
    timeout /t 3 >nul
    start http://localhost
) else (
    echo.
    echo [ERROR] Failed to start Docker containers
    echo Check logs with: %COMPOSE_CMD% logs
    pause
    exit /b 1
)

echo.
pause
