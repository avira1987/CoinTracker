# راهنمای نصب و راه‌اندازی CoinTracker

## پیش‌نیازها

- Docker و Docker Compose نصب شده باشد
- یا Python 3.11+ و Node.js 18+ برای اجرای محلی

## نصب با Docker (توصیه می‌شود)

### 1. بررسی تنظیمات

فایل `settings.json` در root پروژه را بررسی کنید:

```json
{
  "coingecko_api_key": "CG-jDcYH4rngWThu2puTEomdk6Y",
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
```

### 2. ساخت و اجرای کانتینرها

```bash
docker-compose up -d --build
```

### 3. اجرای Migrations

```bash
docker-compose exec backend python manage.py migrate
```

### 4. دسترسی به برنامه

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/
- **Admin Panel**: http://localhost/admin/

### 5. احراز هویت

- **Username**: `admin34_`
- **Password**: `123asd;p+_`

## نصب محلی (بدون Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## استقرار روی سرور

### 1. تغییر تنظیمات

در `backend/config/settings.py`:

```python
ALLOWED_HOSTS = ['your-server-ip', 'your-domain.com']
DEBUG = False
```

### 2. تنظیم متغیرهای محیطی

برای production، از متغیرهای محیطی استفاده کنید:

```bash
export DJANGO_SECRET_KEY='your-secret-key'
export COINGECKO_API_KEY='your-api-key'
```

### 3. اجرای با Docker

```bash
docker-compose up -d
```

### 4. تنظیم Nginx (اختیاری)

اگر از Nginx جداگانه استفاده می‌کنید، فایل `nginx/nginx.conf` را کپی کرده و تنظیمات را انجام دهید.

## استفاده

1. وارد سیستم شوید با `admin34_` / `123asd;p+_`
2. به صفحه Dashboard بروید
3. دکمه "شروع پایش" را بزنید
4. داده‌ها هر دقیقه به‌صورت خودکار به‌روزرسانی می‌شوند
5. برای تغییر تنظیمات، به صفحه Settings بروید

## عیب‌یابی

### مشکل در اتصال WebSocket

- بررسی کنید که Django Channels به درستی نصب شده باشد
- بررسی کنید که port 8000 باز باشد

### مشکل در دریافت داده از API

- بررسی کنید که API key معتبر باشد
- بررسی کنید که اتصال اینترنت برقرار باشد

### مشکل در Docker

```bash
# مشاهده لاگ‌ها
docker-compose logs -f

# راه‌اندازی مجدد
docker-compose restart

# حذف و ساخت مجدد
docker-compose down
docker-compose up -d --build
```

## پشتیبانی

در صورت بروز مشکل، لاگ‌های سیستم را بررسی کنید:

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Nginx logs
docker-compose logs nginx
```

