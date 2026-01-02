@echo off
chcp 65001 >nul
title CoinTracker - توقف پروژه
color 0C

echo.
echo ========================================
echo    🪙 CoinTracker - توقف پروژه
echo ========================================
echo.

REM بررسی مسیر پروژه
if not exist "docker-compose.yml" (
    echo ❌ خطا: فایل docker-compose.yml یافت نشد!
    pause
    exit /b 1
)

REM بررسی وجود Docker
docker --version >nul 2>&1
if %errorlevel% == 0 (
    docker-compose --version >nul 2>&1
    if %errorlevel% == 0 (
        echo 🐳 در حال توقف کانتینرهای Docker...
        docker-compose down
        if %errorlevel% == 0 (
            echo ✅ کانتینرها با موفقیت متوقف شدند.
        ) else (
            echo ⚠️  خطا در توقف کانتینرها
        )
    )
) else (
    echo ⚠️  Docker نصب نشده است - پروژه به صورت محلی اجرا می‌شود
    echo.
    echo 📝 لطفاً پنجره‌های Backend و Frontend را به صورت دستی ببندید.
    echo    یا از Task Manager استفاده کنید.
)

echo.
echo ========================================
pause
