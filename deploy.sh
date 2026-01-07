#!/bin/bash

# CoinTracker - Single File Deployment Script
# این اسکریپت برای راه‌اندازی سریع پروژه روی سیستم‌های دیگر با Docker طراحی شده است

set -e

echo "========================================="
echo "   CoinTracker - Deployment Script"
echo "========================================="
echo ""

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# بررسی نصب Docker
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed!${NC}"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

echo -e "${GREEN}[OK] Docker is installed${NC}"

# بررسی نصب Docker Compose
echo "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}[ERROR] Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose"
    exit 1
fi

echo -e "${GREEN}[OK] Docker Compose is available${NC}"

# بررسی docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}[ERROR] docker-compose.yml not found!${NC}"
    echo "Please make sure you're in the project root directory"
    exit 1
fi

# ایجاد settings.json در صورت عدم وجود
if [ ! -f "settings.json" ]; then
    echo ""
    echo -e "${YELLOW}[INFO] settings.json not found${NC}"
    echo "Creating settings.json from settings.example.json..."
    
    if [ -f "settings.example.json" ]; then
        cp settings.example.json settings.json
        echo -e "${GREEN}[OK] settings.json created${NC}"
        echo ""
        echo -e "${YELLOW}[IMPORTANT] Please edit settings.json and add your CoinGecko API key!${NC}"
        echo "You can get a free API key from: https://www.coingecko.com/api"
        echo ""
        read -p "Press Enter to continue after adding your API key, or Ctrl+C to exit..."
    else
        echo -e "${YELLOW}[WARNING] settings.example.json not found, creating default settings.json${NC}"
        cat > settings.json << 'EOF'
{
  "coingecko_api_key": "YOUR_API_KEY_HERE",
  "default_top_coins": 100,
  "default_weights": {
    "price_change": 0.4,
    "volume_change": 0.3,
    "stability": 0.2,
    "market_cap": 0.1
  },
  "default_data_history_days": 7,
  "update_interval_seconds": 60
}
EOF
        echo -e "${YELLOW}[IMPORTANT] Please edit settings.json and add your CoinGecko API key!${NC}"
        read -p "Press Enter to continue after adding your API key, or Ctrl+C to exit..."
    fi
else
    echo -e "${GREEN}[OK] settings.json exists${NC}"
fi

# توقف کانتینرهای قبلی در صورت وجود
echo ""
echo "Stopping any existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

# Build و اجرای کانتینرها
echo ""
echo "Building and starting Docker containers..."
echo "This may take a few minutes on first run..."
echo ""

if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
    COMPOSE_CMD="docker-compose"
else
    docker compose up -d --build
    COMPOSE_CMD="docker compose"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}[SUCCESS] Project started successfully!${NC}"
    echo ""
    echo "Waiting for services to be ready..."
    sleep 5
    
    echo ""
    echo "========================================="
    echo "   Application Access"
    echo "========================================="
    echo ""
    echo "Frontend:    http://localhost"
    echo "Backend API: http://localhost/api/"
    echo "Admin Panel: http://localhost/admin/"
    echo ""
    echo "========================================="
    echo "   Default Login Credentials"
    echo "========================================="
    echo ""
    echo "Username: admin34_"
    echo "Password: 123asd;p+_"
    echo ""
    echo -e "${YELLOW}[SECURITY] Please change the default password in production!${NC}"
    echo ""
    echo "========================================="
    echo "   Useful Commands"
    echo "========================================="
    echo ""
    echo "View logs:        $COMPOSE_CMD logs -f"
    echo "Stop services:    $COMPOSE_CMD down"
    echo "Restart services: $COMPOSE_CMD restart"
    echo "View status:      $COMPOSE_CMD ps"
    echo ""
    
    # بررسی وضعیت کانتینرها
    echo "Container status:"
    $COMPOSE_CMD ps
    echo ""
    
else
    echo ""
    echo -e "${RED}[ERROR] Failed to start Docker containers${NC}"
    echo "Check logs with: $COMPOSE_CMD logs"
    exit 1
fi
