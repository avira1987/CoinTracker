# Changelog

تمام تغییرات مهم این پروژه در این فایل مستند می‌شود.

فرمت بر اساس [Keep a Changelog](https://keepachangelog.com/fa/1.0.0/) و
این پروژه از [Semantic Versioning](https://semver.org/lang/fa/) پیروی می‌کند.

## [1.0.0] - 2024-01-XX

### اضافه شده
- سیستم رتبه‌بندی داینامیک ارزهای دیجیتال با الگوریتم وزنی
- رابط کاربری فارسی کامل با React
- به‌روزرسانی Real-time از طریق WebSocket
- صفحه تنظیمات پیشرفته با بخش‌بندی
- سیستم احراز هویت ساده با session-based authentication
- پایش خودکار با قابلیت Start/Stop
- پشتیبانی کامل از Docker و Docker Compose
- ذخیره تاریخچه قیمت‌ها برای محاسبه پایداری
- محاسبه پایداری ترکیبی (واریانس، ثبات روند، ریسک برگشت)
- نمایش دلیل رتبه‌بندی برای هر کوین
- API RESTful کامل با Django REST Framework
- Background task scheduler با APScheduler
- پشتیبانی از CoinGecko API
- مستندات کامل (README, CONTRIBUTING, INSTALL)

### تکنولوژی‌ها
- Django 4.2 + Django REST Framework
- React 18 + Vite
- Django Channels برای WebSocket
- SQLite Database
- Nginx برای Reverse Proxy
- Docker & Docker Compose

### ویژگی‌های رتبه‌بندی
- تغییرات قیمت (وزن پیش‌فرض: 40%)
- تغییرات حجم (وزن پیش‌فرض: 30%)
- پایداری (وزن پیش‌فرض: 20%)
- حجم بازار (وزن پیش‌فرض: 10%)

### تنظیمات قابل تغییر
- وزن‌های رتبه‌بندی
- تعداد کوین‌های نمایش داده شده
- روزهای تاریخچه برای محاسبه پایداری
- فاصله به‌روزرسانی خودکار
- کلید API CoinGecko

---

## [Unreleased]

### برنامه‌ریزی شده
- پشتیبانی از چندین API (CoinMarketCap, Binance)
- نمودارهای قیمت و حجم
- فیلتر و جستجوی پیشرفته
- اعلان‌های Real-time برای تغییرات بزرگ
- Export داده‌ها به CSV/Excel
- پشتیبانی از چندین زبان
- Dark mode
- Mobile responsive design
- Unit tests و Integration tests
- CI/CD pipeline

---

[1.0.0]: https://github.com/avira1987/CoinTracker/releases/tag/v1.0.0
