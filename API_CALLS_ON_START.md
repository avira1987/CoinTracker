# API‌های فراخوانی شده هنگام شروع پایش

## خلاصه
وقتی کاربر روی دکمه **"شروع پایش"** کلیک می‌کند، سیستم به ترتیب زیر API‌های زیر را فراخوانی می‌کند:

---

## 1️⃣ API داخلی (Backend)
**Endpoint:** `POST /api/monitoring/start/`
- **فایل:** `backend/api/views.py` - خط 119-154
- **عملکرد:** شروع scheduler و اجرای فوری اولین به‌روزرسانی

---

## 2️⃣ CoinGecko API - لیست کوین‌های برتر
**Endpoint:** `GET https://api.coingecko.com/api/v3/coins/markets`
- **فایل:** `backend/services/coingecko_service.py` - خط 28-48
- **متد:** `get_top_coins()`
- **پارامترها:**
  - `vs_currency`: usd
  - `order`: market_cap_desc
  - `per_page`: تعداد کوین‌ها (از تنظیمات)
  - `price_change_percentage`: 1h,24h,7d
- **زمان فراخوانی:** بلافاصله بعد از شروع پایش (در `update_task()`)

---

## 3️⃣ API خارجی Standing - API دوم
**Endpoint:** `GET http://87.107.108.95:8000/standing`
- **فایل:** `backend/services/coingecko_service.py` - خط 72-101
- **متد:** `get_standing_data()`
- **Headers:**
  - `X-API-Key`: xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI
- **پارامترها:**
  - `limit`: 10000
  - `offset`: 0
- **زمان فراخوانی:** در `update_cryptocurrencies()` - خط 115
- **⚠️ توجه:** این API در `coingecko_service` استفاده می‌شود اما در `standing_service` از API دیگری استفاده می‌شود!

---

## 4️⃣ CoinGecko API - جزئیات هر کوین
**Endpoint:** `GET https://api.coingecko.com/api/v3/coins/{coin_id}`
- **فایل:** `backend/services/coingecko_service.py` - خط 50-70
- **متد:** `get_coin_details(coin_id)`
- **پارامترها:**
  - `localization`: False
  - `tickers`: False
  - `market_data`: True
  - `community_data`: False
  - `developer_data`: False
  - `sparkline`: False
- **زمان فراخوانی:** برای هر کوین در لیست (در حلقه `update_cryptocurrencies()` - خط 146)
- **تعداد فراخوانی:** برابر با تعداد کوین‌های برتر (معمولاً 100 کوین)

---

## 5️⃣ API خارجی Standing - API اول
**Endpoint:** `GET http://81.168.119.209:8000/standing`
- **فایل:** `backend/services/standing_service.py` - خط 120-186
- **متد:** `fetch_and_update_standing()`
- **Headers:**
  - `X-API-Key`: FOTHB4y_kZPc08eCcwdSe19bFdYEOGm51zuw6I8V-ek
- **پارامترها:**
  - `limit`: 10000
  - `offset`: 0
- **زمان فراخوانی:** بلافاصله بعد از شروع پایش (در `update_standing_task()` - خط 197)
- **Cache:** این API از cache استفاده می‌کند (1 ساعت)

---

## 6️⃣ Ranking Service (بدون API خارجی)
**فایل:** `backend/services/ranking_service.py` - خط 194-226
- **متد:** `update_rankings()`
- **عملکرد:** محاسبه داخلی رتبه‌بندی بر اساس فرمول وزن‌دار
- **⚠️ هیچ API خارجی فراخوانی نمی‌کند** - فقط محاسبات داخلی

---

## ترتیب اجرا

```
1. کاربر کلیک می‌کند → POST /api/monitoring/start/
2. scheduler.start_monitoring() اجرا می‌شود
3. بلافاصله update_task() اجرا می‌شود:
   ├─ CoinGecko: GET /coins/markets (لیست کوین‌ها)
   ├─ Standing API 2: GET http://87.107.108.95:8000/standing
   ├─ برای هر کوین: CoinGecko GET /coins/{coin_id} (جزئیات)
   └─ RankingService.update_rankings() (محاسبات داخلی)
4. همزمان update_standing_task() اجرا می‌شود:
   └─ Standing API 1: GET http://81.168.119.209:8000/standing
```

---

## ⚠️ مشکلات شناسایی شده

### 1. استفاده از دو API مختلف برای Standing
- `coingecko_service` از **API 2** (`87.107.108.95`) استفاده می‌کند
- `standing_service` از **API 1** (`81.168.119.209`) استفاده می‌کند
- این باعث می‌شود داده‌های standing از دو منبع مختلف دریافت شوند

### 2. فراخوانی تکراری Standing API
- Standing API در `update_cryptocurrencies()` فراخوانی می‌شود
- Standing API دوباره در `update_standing_task()` فراخوانی می‌شود
- این می‌تواند باعث overhead غیرضروری شود

---

## فایل‌های مرتبط

- `frontend/src/pages/Dashboard.jsx` - خط 227-242 (فراخوانی startMonitoring)
- `frontend/src/services/api.js` - خط 147-151 (تابع startMonitoring)
- `backend/api/views.py` - خط 119-154 (start_monitoring_view)
- `backend/tasks/scheduler.py` - خط 113-144 (start_monitoring)
- `backend/services/coingecko_service.py` - تمام فایل
- `backend/services/standing_service.py` - تمام فایل
- `backend/services/ranking_service.py` - خط 194-226

---

## خلاصه تعداد فراخوانی‌ها

| API | تعداد فراخوانی | زمان |
|-----|----------------|------|
| CoinGecko `/coins/markets` | 1 | بلافاصله |
| CoinGecko `/coins/{id}` | ~100 (تعداد کوین‌ها) | بلافاصله |
| Standing API 1 | 1 | بلافاصله |
| Standing API 2 | 1 | بلافاصله |

**جمع کل:** ~103 فراخوانی API خارجی در شروع پایش
