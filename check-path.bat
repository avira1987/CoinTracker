@echo off
echo.
echo ========================================
echo    CoinTracker - Path Checker
echo ========================================
echo.

echo Current directory:
cd
echo.

echo Checking for docker-compose.yml...
if exist docker-compose.yml (
    echo [OK] docker-compose.yml found in current directory!
    echo.
    echo Directory contents:
    dir /b
) else (
    echo [ERROR] docker-compose.yml NOT found!
    echo.
    echo Please make sure you are in the project root directory.
    echo.
    echo Looking in parent directories...
    cd ..
    if exist docker-compose.yml (
        echo [FOUND] docker-compose.yml is in parent directory!
        cd
        echo Current path: %CD%
    ) else (
        cd ..
        if exist docker-compose.yml (
            echo [FOUND] docker-compose.yml is two levels up!
            cd
            echo Current path: %CD%
        ) else (
            echo [ERROR] docker-compose.yml not found in nearby directories!
            echo.
            echo Please navigate to the correct project directory.
        )
    )
)

echo.
pause
