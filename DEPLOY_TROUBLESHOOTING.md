# 🔧 رفع مشکل خطای "\CoinTracker-main was unexpected at this time"

## مشکل

این خطا معمولاً در Windows batch files رخ می‌دهد و چند علت ممکن دارد:

## راه‌حل‌ها

### 1. تغییر نام پوشه

اگر پوشه پروژه `CoinTracker-main` نام دارد (بعد از دانلود از GitHub)، نام آن را به `CoinTracker` تغییر دهید:

```cmd
ren CoinTracker-main CoinTracker
cd CoinTracker
```

### 2. استفاده از نسخه ایمن batch file

از فایل `deploy-safe.bat` به جای `deploy.bat` استفاده کنید:

```cmd
deploy-safe.bat
```

### 3. اجرای مستقیم docker-compose

اگر batch file کار نمی‌کند، مستقیماً از docker-compose استفاده کنید:

```cmd
docker-compose up -d --build
```

یا اگر docker compose plugin دارید:

```cmd
docker compose up -d --build
```

### 4. بررسی مسیر

مطمئن شوید در مسیر صحیح هستید و هیچ کاراکتر خاصی در مسیر وجود ندارد:

```cmd
cd /d "C:\path\to\CoinTracker"
dir
```

### 5. استفاده از PowerShell

به جای CMD از PowerShell استفاده کنید:

```powershell
cd "C:\path\to\CoinTracker"
docker-compose up -d --build
```

### 6. بررسی فضای خالی

مطمئن شوید که در مسیر پروژه از فاصله (space) استفاده نمی‌شود:

❌ بد: `C:\My Projects\CoinTracker-main`
✅ خوب: `C:\Projects\CoinTracker`

## علت مشکل

این خطا معمولاً به دلیل:
- استفاده از کاراکترهای خاص در نام پوشه (مثل `-main`)
- مشکل در parsing متغیرها در batch file
- مشکل با backslash در مسیرها
- مشکل با delayed expansion در batch files

## راه‌حل سریع

1. پوشه را به `CoinTracker` تغییر نام دهید
2. از `deploy-safe.bat` استفاده کنید
3. یا مستقیماً `docker-compose up -d --build` اجرا کنید
