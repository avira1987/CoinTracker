# ساختار پروژه CoinTracker

این سند ساختار کامل پروژه را توضیح می‌دهد.

## 📁 ساختار کلی

```
CoinTracker/
├── .github/                    # تنظیمات GitHub
│   ├── ISSUE_TEMPLATE/        # قالب‌های Issue
│   ├── workflows/             # GitHub Actions
│   ├── FUNDING.yml            # اطلاعات حمایت مالی
│   └── pull_request_template.md
├── backend/                   # Django Backend
│   ├── api/                   # API Endpoints
│   ├── config/                # تنظیمات Django
│   ├── models/                # مدل‌های دیتابیس
│   ├── services/              # سرویس‌های کسب و کار
│   ├── tasks/                 # Background Tasks
│   ├── websocket/             # WebSocket Handlers
│   ├── manage.py              # Django Management
│   └── requirements.txt       # Python Dependencies
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── pages/             # صفحات اصلی
│   │   ├── services/          # سرویس‌های API و WebSocket
│   │   └── ...
│   ├── package.json           # Node Dependencies
│   └── vite.config.js        # تنظیمات Vite
├── nginx/                     # تنظیمات Nginx
├── docker-compose.yml         # Docker Compose Config
├── Dockerfile.backend         # Backend Dockerfile
├── Dockerfile.frontend        # Frontend Dockerfile
├── settings.json              # تنظیمات برنامه
└── README.md                  # مستندات اصلی
```

## 🔧 Backend Structure

### `/backend/api/`
- **views.py**: تمام API endpoints
- **serializers.py**: Serializers برای تبدیل داده‌ها
- **urls.py**: URL routing برای API
- **authentication.py**: سیستم احراز هویت

### `/backend/models/`
- **coin_models.py**: 
  - `Cryptocurrency`: اطلاعات اصلی کوین‌ها
  - `PriceHistory`: تاریخچه قیمت‌ها
  - `Settings`: تنظیمات سیستم
  - `MonitoringStatus`: وضعیت پایش

### `/backend/services/`
- **coingecko_service.py**: دریافت داده از CoinGecko API
- **ranking_service.py**: الگوریتم رتبه‌بندی

### `/backend/tasks/`
- **scheduler.py**: Background task scheduler با APScheduler

### `/backend/websocket/`
- **consumers.py**: WebSocket consumers برای Real-time updates
- **routing.py**: WebSocket URL routing

### `/backend/config/`
- **settings.py**: تنظیمات اصلی Django
- **asgi.py**: ASGI config برای Channels
- **urls.py**: URL routing اصلی

## 🎨 Frontend Structure

### `/frontend/src/pages/`
- **Dashboard.jsx**: صفحه اصلی با جدول کوین‌ها
- **Settings.jsx**: صفحه تنظیمات
- **Login.jsx**: صفحه ورود

### `/frontend/src/services/`
- **api.js**: سرویس API برای ارتباط با Backend
- **websocket.js**: سرویس WebSocket برای Real-time updates

## 🐳 Docker Structure

### `docker-compose.yml`
سه سرویس اصلی:
- **backend**: Django application
- **frontend**: React application (built)
- **nginx**: Reverse proxy

### `Dockerfile.backend`
- Python 3.11
- نصب dependencies
- اجرای migrations

### `Dockerfile.frontend`
- Node.js 18
- Build React app
- Serve با Nginx

## ⚙️ Configuration Files

### `settings.json`
تنظیمات اصلی برنامه:
- API Key
- وزن‌های رتبه‌بندی
- تعداد کوین‌ها
- فاصله به‌روزرسانی

### `nginx/nginx.conf`
- Reverse proxy برای Backend
- Serve static files برای Frontend
- WebSocket proxy

## 📊 Data Flow

```
User Request
    ↓
Nginx (Port 80)
    ↓
Frontend (React) ←→ Backend API (Django)
    ↓                    ↓
WebSocket ←→ Django Channels
    ↓                    ↓
Real-time Updates    CoinGecko API
    ↓                    ↓
Database (SQLite)    Background Tasks
```

## 🔄 Update Flow

```
1. Background Task (هر 60 ثانیه)
   ↓
2. CoinGecko API → دریافت داده
   ↓
3. Update Database → ذخیره داده‌ها
   ↓
4. Ranking Service → محاسبه رتبه‌بندی
   ↓
5. WebSocket → ارسال به کلاینت‌ها
   ↓
6. Frontend → نمایش به کاربر
```

## 📝 Key Files

### Backend
- `backend/services/ranking_service.py`: قلب سیستم رتبه‌بندی
- `backend/tasks/scheduler.py`: مدیریت Background tasks
- `backend/api/views.py`: تمام API endpoints

### Frontend
- `frontend/src/pages/Dashboard.jsx`: رابط کاربری اصلی
- `frontend/src/services/websocket.js`: مدیریت Real-time updates

## 🗄️ Database Schema

### Cryptocurrency
- اطلاعات اصلی هر کوین
- رتبه و نمره رتبه‌بندی
- تغییرات قیمت و حجم

### PriceHistory
- تاریخچه قیمت‌ها
- برای محاسبه پایداری

### Settings
- تنظیمات سیستم (فقط یک رکورد)

### MonitoringStatus
- وضعیت پایش (فقط یک رکورد)

---

برای اطلاعات بیشتر، به [README.md](README.md) مراجعه کنید.
