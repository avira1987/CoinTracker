@echo off
chcp 65001 >nul
title CoinTracker - Project Setup
color 0A

echo.
echo ========================================
echo    🪙 CoinTracker - Project Setup
echo ========================================
echo.

REM Check project path
if not exist "docker-compose.yml" (
    echo ❌ Error: docker-compose.yml file not found!
    echo Please run this file in the project root directory.
    pause
    exit /b 1
)

REM Check Docker installation
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Docker is installed
    echo.
    echo 🐳 Starting with Docker...
    echo.
    
    REM Check docker-compose installation
    docker-compose --version >nul 2>&1
    if %errorlevel% == 0 (
        echo 📦 Building and running containers...
        docker-compose up -d --build
        
        if %errorlevel% == 0 (
            echo.
            echo ⏳ Waiting for services to start...
            timeout /t 3 >nul
            echo.
            echo 📋 Checking container status and ports...
            docker-compose ps
            echo.
            echo ✅ Project started successfully!
            echo.
            echo 🌐 Application access:
            echo    Frontend: http://localhost:3000
            echo    Backend API: http://localhost:8000/api/
            echo    Admin Panel: http://localhost:8000/admin/
            echo.
            echo 👤 Default login credentials:
            echo    Username: admin34_
            echo    Password: 123asd;p+_
            echo.
            echo 📊 To view logs: docker-compose logs -f
            echo 🛑 To stop: docker-compose down
            echo.
            echo ⏳ Waiting for services to be ready...
            timeout /t 5 >nul
            echo.
            echo 🌐 Opening browser at http://localhost:3000...
            start http://localhost:3000
        ) else (
            echo.
            echo ❌ Error starting Docker!
            echo Please check logs: docker-compose logs
        )
    ) else (
        echo ❌ docker-compose not found!
        echo Please install Docker Compose.
        goto :local_setup
    )
) else (
    echo ⚠️  Docker is not installed
    echo.
    echo 🔄 Starting locally...
    echo.
    goto :local_setup
)

goto :end

:local_setup
echo.
echo 📋 Local setup (without Docker)
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed!
    echo Please install Python 3.11+.
    pause
    exit /b 1
)

REM Check Node.js installation
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed!
    echo Please install Node.js 18+.
    pause
    exit /b 1
)

echo ✅ Python and Node.js are installed
echo.

REM Check if virtual environment exists for Backend
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

echo 🔧 Installing Backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Error installing Backend dependencies
    echo Retrying...
    pip install -r requirements.txt
)

echo 📊 Running migrations...
python manage.py migrate

echo 🚀 Starting Backend...
start "CoinTracker Backend" cmd /k "venv\Scripts\activate.bat && python manage.py runserver"
cd ..

REM Check if node_modules exists for Frontend
if not exist "frontend\node_modules" (
    echo 📦 Installing Frontend dependencies...
    cd frontend
    call npm install
    cd ..
) else (
    echo ✅ Frontend dependencies are installed
)

echo 🚀 Starting Frontend...
cd frontend
start "CoinTracker Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ✅ Project started successfully!
echo.
echo 🌐 Application access:
echo    Frontend: http://localhost:6000
echo    Backend API: http://localhost:8000/api/
echo    Admin Panel: http://localhost:8000/admin/
echo.
echo 👤 Default login credentials:
echo    Username: admin34_
echo    Password: 123asd;p+_
echo.
echo 📝 Note: Two new windows have been opened for Backend and Frontend.
echo    To stop, close the windows or press Ctrl+C.
echo.

timeout /t 5 >nul
start http://localhost:6000

:end
echo.
echo ========================================
pause
