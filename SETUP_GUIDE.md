# 🚀 راهنمای راه‌اندازی سریع - حل مشکل "no configuration file provided"

## ⚠️ مشکل: "no configuration file provided: not found"

این خطا زمانی رخ می‌دهد که:
- فایل `docker-compose.yml` در مسیر فعلی وجود ندارد
- در پوشه اشتباه هستید

## ✅ راه‌حل سریع

### روش 1: بررسی مسیر

```cmd
# بررسی کنید docker-compose.yml وجود دارد
dir docker-compose.yml

# یا از اسکریپت کمکی استفاده کنید
check-path.bat
```

### روش 2: یافتن مسیر صحیح

```cmd
# اگر در CoinTracker-main (3)\CoinTracker-main هستید
cd ..
dir docker-compose.yml

# یا دو سطح بالا بروید
cd ..\..
dir docker-compose.yml
```

### روش 3: استفاده از deploy script

```cmd
# از deploy.bat استفاده کنید که خودش مسیر را درست می‌کند
deploy.bat
```

### روش 4: دستور با مسیر کامل

```cmd
# اگر docker-compose.yml در مسیر مشخصی است
docker-compose -f "C:\path\to\CoinTracker\docker-compose.yml" up -d
```

## 📁 ساختار صحیح پروژه

پوشه پروژه باید شامل این فایل‌ها باشد:

```
CoinTracker/
├── docker-compose.yml      ← این فایل باید اینجا باشد
├── Dockerfile.backend
├── Dockerfile.frontend
├── settings.json
├── backend/
├── frontend/
└── nginx/
```

## 🔍 چک کردن ساختار

```cmd
# لیست فایل‌های root
dir /b

# باید این فایل‌ها را ببینید:
# - docker-compose.yml
# - Dockerfile.backend
# - Dockerfile.frontend
# - settings.json (یا settings.example.json)
# - backend/
# - frontend/
```

## 💡 نکات مهم

1. **پوشه تودرتو**: اگر بعد از دانلود از GitHub پوشه‌ها تودرتو شدند:
   ```cmd
   # مثال: CoinTracker-main (3)\CoinTracker-main
   # باید به CoinTracker-main بروید
   cd ..
   ```

2. **فاصله در نام**: اگر فاصله در مسیر دارید، از quotes استفاده کنید:
   ```cmd
   cd "C:\Users\Administrator\Desktop\CoinTracker-main"
   ```

3. **استفاده از deploy script**: همیشه از `deploy.bat` استفاده کنید که همه چیز را بررسی می‌کند.

## 🎯 دستورات پیشنهادی

```cmd
# 1. پیدا کردن مسیر صحیح
cd C:\Users\Administrator\Desktop
dir /s docker-compose.yml

# 2. رفتن به مسیر پیدا شده
cd "CoinTracker-main"

# 3. بررسی فایل‌ها
dir docker-compose.yml

# 4. اجرای docker-compose
docker-compose up -d --build
```

## ❓ اگر هنوز مشکل دارید

1. کل پروژه را دوباره از GitHub دانلود کنید
2. به پوشه root پروژه بروید (جایی که docker-compose.yml است)
3. از `deploy.bat` استفاده کنید
