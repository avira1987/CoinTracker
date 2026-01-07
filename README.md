# 🪙 CoinTracker - سیستم رتبه‌بندی هوشمند ارزهای دیجیتال

[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

پروژه وب‌بیسی پیشرفته برای نمایش و رتبه‌بندی ارزهای دیجیتال بر اساس الگوریتم‌های هوشمند و داده‌های Real-time از [CoinGecko API](https://www.coingecko.com/).

## ✨ ویژگی‌ها

- 🎯 **رتبه‌بندی داینامیک**: الگوریتم وزنی قابل تنظیم بر اساس تغییرات قیمت، حجم، پایداری و حجم بازار
- ⚡ **Real-time Updates**: به‌روزرسانی لحظه‌ای از طریق WebSocket هر دقیقه
- 🇮🇷 **رابط کاربری فارسی**: طراحی زیبا و کاربرپسند با پشتیبانی کامل از زبان فارسی
- ⚙️ **تنظیمات پیشرفته**: کنترل کامل بر معیارهای رتبه‌بندی و پارامترهای سیستم
- 🔐 **احراز هویت**: سیستم مدیریت امن با session-based authentication
- 📊 **داشبورد جامع**: نمایش کامل اطلاعات، آمار و دلیل رتبه‌بندی هر کوین
- 🔄 **پایش خودکار**: قابلیت Start/Stop برای کنترل به‌روزرسانی‌های خودکار
- 💾 **ذخیره تاریخچه**: ذخیره داده‌های تاریخی برای محاسبه پایداری

## 🏗️ معماری

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   React     │────▶│   Django     │────▶│  CoinGecko  │
│  Frontend   │◀────│   Backend    │     │     API     │
│             │WS   │              │     └─────────────┘
└─────────────┘     └──────────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   SQLite   │
                     │  Database   │
                     └─────────────┘
```

## 🚀 نصب سریع

### پیش‌نیازها

- Docker & Docker Compose
- یا Python 3.11+ و Node.js 18+
- API Key از [CoinGecko](https://www.coingecko.com/api) (رایگان)

### با Docker (توصیه می‌شود)

#### روش سریع (تک فایل):

**Linux/Mac:**
```bash
chmod +x deploy.sh && ./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

اسکریپت به صورت خودکار همه چیز را راه‌اندازی می‌کند. برای جزئیات بیشتر [DEPLOY.md](DEPLOY.md) یا [QUICK_START.md](QUICK_START.md) را مطالعه کنید.

#### روش دستی:

```bash
# 1. کلون کردن پروژه
git clone https://github.com/avira1987/CoinTracker.git
cd CoinTracker

# 2. تنظیم API Key در settings.json
# فایل settings.json را ویرایش کرده و API Key خود را وارد کنید

# 3. اجرای پروژه
docker-compose up -d --build

# 4. دسترسی به برنامه
# Frontend: http://localhost
# Backend API: http://localhost/api/
# Admin Panel: http://localhost/admin/
```

### نصب محلی

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🔑 احراز هویت پیش‌فرض

- **Username**: `admin34_`
- **Password**: `123asd;p+_`

⚠️ **توجه**: حتماً رمز عبور را در production تغییر دهید!

## 📊 فرمول رتبه‌بندی

```
Score = (PriceChange × 40%) + (VolumeChange × 30%) + 
        (Stability × 20%) + (MarketCap × 10%)
```

### معیارهای رتبه‌بندی

| معیار | وزن پیش‌فرض | توضیحات |
|-------|------------|---------|
| **تغییرات قیمت** | 40% | تغییرات درصدی قیمت در 24 ساعت گذشته |
| **تغییرات حجم** | 30% | تغییرات درصدی حجم معاملات در 24 ساعت |
| **پایداری** | 20% | ترکیبی از واریانس، ثبات روند و ریسک برگشت |
| **حجم بازار** | 10% | نرمال‌سازی شده بر اساس تمام کوین‌ها |

### محاسبه پایداری

پایداری به صورت ترکیبی از سه معیار محاسبه می‌شود:

1. **واریانس تغییرات قیمت**: کوین‌هایی با نوسانات کمتر، پایداری بیشتری دارند
2. **ثبات روند**: تغییرات مداوم در یک جهت نشان‌دهنده پایداری است
3. **ریسک برگشت**: بر اساس نوسانات تاریخی، احتمال برگشت به حالت اولیه محاسبه می‌شود

## 📡 API Documentation

### Authentication
- `POST /api/auth/login/` - ورود به سیستم
- `POST /api/auth/logout/` - خروج از سیستم
- `GET /api/auth/check/` - بررسی وضعیت احراز هویت

### Cryptocurrencies
- `GET /api/coins/` - لیست کوین‌های رتبه‌بندی شده

### Monitoring
- `GET /api/monitoring/status/` - وضعیت پایش
- `POST /api/monitoring/start/` - شروع پایش خودکار
- `POST /api/monitoring/stop/` - توقف پایش
- `POST /api/monitoring/update/` - به‌روزرسانی دستی داده‌ها

### Settings
- `GET /api/settings/` - دریافت تنظیمات سیستم
- `PUT /api/settings/` - به‌روزرسانی تنظیمات

## 🔌 WebSocket

اتصال WebSocket در آدرس `ws://localhost/ws/coins/` برای دریافت به‌روزرسانی‌های Real-time.

### Event Types

- `initial_data` - داده اولیه هنگام اتصال (coins + status)
- `coin_update` - به‌روزرسانی لیست کوین‌ها
- `status_update` - به‌روزرسانی وضعیت پایش
- `error` - خطا در سیستم

### مثال استفاده

```javascript
const ws = new WebSocket('ws://localhost/ws/coins/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'coin_update') {
    console.log('Updated coins:', data.coins);
  }
};
```

## 🛠️ تکنولوژی‌ها

### Backend
- **Django 4.2** - Framework اصلی
- **Django REST Framework** - API RESTful
- **Django Channels** - WebSocket support
- **APScheduler** - Background tasks
- **SQLite** - Database

### Frontend
- **React 18** - UI Framework
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Reconnecting WebSocket** - WebSocket client

### DevOps
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy & Web server

## 📁 ساختار پروژه

```
CoinTracker/
├── backend/                 # Django Backend
│   ├── api/                 # API Endpoints
│   │   ├── views.py         # API Views
│   │   ├── serializers.py  # Data Serializers
│   │   └── urls.py          # URL Routing
│   ├── models/              # Database Models
│   │   └── coin_models.py  # Cryptocurrency Models
│   ├── services/            # Business Logic
│   │   ├── coingecko_service.py    # CoinGecko API Service
│   │   └── ranking_service.py      # Ranking Algorithm
│   ├── tasks/               # Background Tasks
│   │   └── scheduler.py     # Task Scheduler
│   ├── websocket/           # WebSocket Handlers
│   │   ├── consumers.py     # WebSocket Consumers
│   │   └── routing.py       # WebSocket Routing
│   └── config/              # Django Settings
├── frontend/                # React Frontend
│   └── src/
│       ├── pages/           # Page Components
│       │   ├── Dashboard.jsx
│       │   ├── Settings.jsx
│       │   └── Login.jsx
│       └── services/        # API & WebSocket Clients
│           ├── api.js
│           └── websocket.js
├── nginx/                   # Nginx Configuration
├── docker-compose.yml       # Docker Compose Config
├── Dockerfile.backend       # Backend Dockerfile
├── Dockerfile.frontend      # Frontend Dockerfile
└── settings.json            # Application Settings
```

## ⚙️ تنظیمات

تمام تنظیمات در صفحه Settings قابل تغییر هستند:

- **کلید API CoinGecko**: برای دریافت داده از API
- **وزن‌های رتبه‌بندی**: تنظیم وزن هر معیار (مجموع باید 1 باشد)
- **تعداد کوین‌های برتر**: تعداد کوین‌هایی که نمایش داده می‌شوند (پیش‌فرض: 100)
- **روزهای تاریخچه**: تعداد روزهای داده تاریخی برای محاسبه پایداری (پیش‌فرض: 7)
- **فاصله به‌روزرسانی**: فاصله زمانی به‌روزرسانی خودکار به ثانیه (پیش‌فرض: 60)

## 🚀 استقرار روی سرور

برای استقرار روی سرور با IP معتبر:

1. **تغییر تنظیمات Django**:
   ```python
   # backend/config/settings.py
   ALLOWED_HOSTS = ['your-server-ip', 'your-domain.com']
   DEBUG = False
   ```

2. **تنظیم متغیرهای محیطی**:
   ```bash
   export DJANGO_SECRET_KEY='your-secret-key'
   export COINGECKO_API_KEY='your-api-key'
   ```

3. **اجرای با Docker**:
   ```bash
   docker-compose up -d
   ```

4. **استفاده از SSL/TLS** (توصیه می‌شود):
   - تنظیم Nginx برای HTTPS
   - استفاده از Let's Encrypt

## 🧪 تست

```bash
# Backend Tests
cd backend
python manage.py test

# Frontend Tests (در صورت وجود)
cd frontend
npm test
```

## 🤝 مشارکت

مشارکت‌ها خوش‌آمدند! لطفاً [CONTRIBUTING.md](CONTRIBUTING.md) را مطالعه کنید.

1. Fork کنید
2. Branch جدید بسازید (`git checkout -b feature/AmazingFeature`)
3. Commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. Pull Request باز کنید

## 📝 License

این پروژه تحت مجوز [MIT License](LICENSE) منتشر شده است.

## 👤 نویسنده

**avira1987**

- GitHub: [@avira1987](https://github.com/avira1987)
- Repository: [CoinTracker](https://github.com/avira1987/CoinTracker)

## 🙏 تشکر

- [CoinGecko](https://www.coingecko.com/) برای API عالی و رایگان
- جامعه Open Source برای ابزارها و کتابخانه‌های عالی
- تمام مشارکت‌کنندگان این پروژه

## 📚 مستندات بیشتر

- [راهنمای نصب کامل](INSTALL.md)
- [راهنمای مشارکت](CONTRIBUTING.md)
- [تغییرات نسخه‌ها](CHANGELOG.md)

## 🐛 گزارش باگ

اگر باگی پیدا کردید، لطفاً در [Issues](https://github.com/avira1987/CoinTracker/issues) گزارش دهید.

## 💡 پیشنهاد ویژگی

ایده‌های خود را برای ویژگی‌های جدید در [Issues](https://github.com/avira1987/CoinTracker/issues) به اشتراک بگذارید.

---

⭐ اگر این پروژه برایتان مفید بود، ستاره بدید!

🔗 **لینک پروژه**: https://github.com/avira1987/CoinTracker