# مستندات کامل پروژه CoinTracker

## فهرست مطالب
1. [معرفی پروژه](#معرفی-پروژه)
2. [معماری سیستم](#معماری-سیستم)
3. [نحوه عملکرد سیستم](#نحوه-عملکرد-سیستم)
4. [ساختار درخواست‌های API](#ساختار-درخواست‌های-api)
5. [مدل‌های دیتابیس](#مدل‌های-دیتابیس)
6. [الگوریتم رتبه‌بندی](#الگوریتم-رتبه‌بندی)
7. [سرویس‌های Backend](#سرویس‌های-backend)
8. [ارتباطات Real-Time](#ارتباطات-real-time)
9. [راه‌اندازی و استقرار](#راه‌اندازی-و-استقرار)

---

## معرفی پروژه

**CoinTracker** یک سیستم هوشمند رتبه‌بندی ارزهای دیجیتال است که با استفاده از الگوریتم وزن‌دار پیشرفته، ارزهای دیجیتال را بر اساس معیارهای مختلف رتبه‌بندی می‌کند.

### ویژگی‌های کلیدی
- **رتبه‌بندی دینامیک**: الگوریتم وزن‌دار قابل تنظیم
- **به‌روزرسانی Real-Time**: استفاده از WebSocket
- **رابط کاربری فارسی**: پشتیبانی کامل از زبان فارسی
- **احراز هویت**: سیستم Session-based Authentication
- **نظارت خودکار**: شروع/توقف خودکار به‌روزرسانی‌ها
- **تنظیمات پیشرفته**: قابلیت تنظیم وزن‌ها و پارامترها
- **ذخیره تاریخچه**: برای محاسبه ثبات قیمت

### تکنولوژی‌های استفاده شده

#### Backend
- **Django 4.2**: فریمورک اصلی
- **Django REST Framework**: برای API های RESTful
- **Django Channels**: برای WebSocket
- **APScheduler**: برای وظایف زمان‌بندی شده
- **SQLite**: پایگاه داده
- **Python 3.11+**: زبان برنامه‌نویسی

#### Frontend
- **React 18**: فریمورک UI
- **Vite**: ابزار Build
- **React Router**: مدیریت مسیریابی
- **Axios**: کلاینت HTTP
- **Reconnecting WebSocket**: کلاینت WebSocket

#### DevOps
- **Docker & Docker Compose**: کانتینریزاسیون
- **Nginx**: Reverse Proxy و وب سرور

---

## معماری سیستم

### نمای کلی معماری

```
┌─────────────┐
│   کاربر     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Nginx    │ (Reverse Proxy)
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   React     │   │   Django    │   │  WebSocket  │
│  Frontend   │   │   Backend   │   │   Server    │
└─────────────┘   └──────┬──────┘   └─────────────┘
                         │
                         ├─────────────┬─────────────┐
                         ▼             ▼             ▼
                  ┌─────────────┐ ┌──────────┐ ┌──────────┐
                  │  CoinGecko  │ │  SQLite  │ │ Standing │
                  │     API     │ │    DB    │ │   APIs   │
                  └─────────────┘ └──────────┘ └──────────┘
```

### ساختار دایرکتوری

```
CoinTracker/
├── backend/
│   ├── api/              # API Endpoints و Views
│   ├── config/           # تنظیمات Django
│   ├── models/           # مدل‌های Database
│   ├── services/         # سرویس‌های Business Logic
│   ├── tasks/            # وظایف زمان‌بندی شده
│   └── websocket/        # WebSocket Consumers
├── frontend/
│   └── src/
│       ├── pages/        # کامپوننت‌های صفحات
│       └── services/     # سرویس‌های API و WebSocket
├── nginx/                # تنظیمات Nginx
└── docker-compose.yml    # تنظیمات Docker
```

---

## نحوه عملکرد سیستم

### 1. جریان داده (Data Flow)

#### مرحله اول: دریافت داده
1. **Scheduler** هر 5 دقیقه (پیش‌فرض) اجرا می‌شود
2. **CoinGeckoService** درخواست به API CoinGecko می‌فرستد
3. داده‌های Top Coins دریافت می‌شود
4. **StandingService** به APIهای خارجی Social Standing درخواست می‌فرستد
5. داده‌های Standing (رتبه اجتماعی) دریافت و Cache می‌شود

#### مرحله دوم: پردازش و ذخیره‌سازی
1. برای هر Coin، اطلاعات تفصیلی از CoinGecko دریافت می‌شود
2. محاسبه **Volume Change 24h**:
   ```python
   volume_change_24h = ((current_volume - previous_volume) / previous_volume) * 100
   ```
3. ذخیره در مدل `Cryptocurrency`
4. ذخیره تاریخچه در مدل `PriceHistory`

#### مرحله سوم: رتبه‌بندی
1. **RankingService** فعال می‌شود
2. محاسبه **Stability Score** بر اساس تاریخچه
3. نرمال‌سازی تمام معیارها (0-100)
4. محاسبه **Rank Score** با فرمول وزن‌دار
5. مرتب‌سازی و اختصاص رتبه

#### مرحله چهارم: انتشار
1. ذخیره در Database
2. ارسال به تمام کلاینت‌های WebSocket متصل
3. به‌روزرسانی UI به صورت Real-Time

### 2. الگوریتم رتبه‌بندی (Ranking Algorithm)

#### فرمول کلی
```
Rank Score = (W₁ × Price Change) + (W₂ × Volume Change) + 
             (W₃ × Stability) + (W₄ × Market Cap) + 
             (W₅ × Social Standing)
```

#### وزن‌های پیش‌فرض
- Price Change: 25%
- Volume Change: 20%
- Stability: 25%
- Market Cap: 15%
- Social Standing: 15%

#### محاسبه Stability Score

**Stability Score** یک معیار ترکیبی است که شامل:

1. **Variance Score (40%)**: واریانس تغییرات قیمت 24 ساعته
   ```python
   price_changes = [history.price_change_24h for history in last_7_days]
   variance = statistics.variance(price_changes)
   variance_score = max(0, 100 - (variance * 2))
   ```

2. **Trend Consistency (30%)**: ثبات روند
   ```python
   positive_changes = len([x for x in price_changes if x > 0])
   negative_changes = len([x for x in price_changes if x < 0])
   consistency = abs(positive_changes - negative_changes) / total_days
   trend_score = consistency * 100
   ```

3. **Reversion Risk (30%)**: ریسک بازگشت قیمت
   ```python
   recent_trend = mean(last_3_days_changes)
   overall_trend = mean(all_changes)
   divergence = abs(recent_trend - overall_trend)
   reversion_score = max(0, 100 - (divergence * 3))
   ```

#### نرمال‌سازی معیارها

**Price Change Normalization**:
```python
def normalize_price_change(change):
    min_change = -50  # حداکثر کاهش
    max_change = 200  # حداکثر افزایش
    normalized = ((change - min_change) / (max_change - min_change)) * 100
    return max(0, min(100, normalized))
```

**Volume Change Normalization**:
```python
def normalize_volume_change(change):
    min_change = -80
    max_change = 500
    normalized = ((change - min_change) / (max_change - min_change)) * 100
    return max(0, min(100, normalized))
```

**Market Cap Normalization**:
```python
def normalize_market_cap(market_cap):
    if market_cap <= 0:
        return 0
    log_cap = math.log10(market_cap)
    min_log = 6   # $1M
    max_log = 12  # $1T
    normalized = ((log_cap - min_log) / (max_log - min_log)) * 100
    return max(0, min(100, normalized))
```

**Standing Normalization**:
```python
def normalize_standing(standing):
    # Standing از 1 (بهترین) تا 1000+ (بدترین)
    if standing <= 0:
        return 0
    normalized = max(0, 100 - (standing / 10))
    return max(0, min(100, normalized))
```

### 3. سیستم Cache و Fallback

#### Social API Cache
برای بهبود عملکرد و کاهش درخواست‌ها:

```python
# Cache Duration: 1 ساعت
CACHE_DURATION = timedelta(hours=1)

# در SocialAPICache Model:
def is_cache_valid(self):
    if not self.last_successful_request or not self.cached_data:
        return False
    return timezone.now() - self.last_successful_request < CACHE_DURATION
```

#### Fallback Mechanism
در صورت عدم دسترسی به API اول، از API دوم استفاده می‌شود:

```python
# در StandingService:
def fetch_and_update_standing():
    # تلاش برای API اول
    try:
        indicators_1 = fetch_from_api(STANDING_API_URL_1)
    except Exception:
        indicators_1 = None
    
    # Fallback به API دوم
    try:
        indicators_2 = fetch_from_api(STANDING_API_URL_2)
    except Exception:
        indicators_2 = None
    
    # ادغام نتایج
    merged = merge_indicators(indicators_1, indicators_2)
```

---

## ساختار درخواست‌های API

### Base URL
- **توسعه**: `http://localhost:8000/api`
- **تولید**: `http://your-domain.com/api`

### Authentication

#### ورود (Login)
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response 200:
{
  "status": "success",
  "message": "Login successful"
}
```

#### خروج (Logout)
```http
POST /api/auth/logout/

Response 200:
{
  "status": "success",
  "message": "Logout successful"
}
```

#### بررسی احراز هویت
```http
GET /api/auth/check/

Response 200:
{
  "authenticated": true
}
```

### Cryptocurrencies

#### دریافت لیست ارزها
```http
GET /api/cryptocurrencies/
Query Parameters:
  - page: شماره صفحه (پیش‌فرض: 1)
  - page_size: تعداد آیتم در صفحه (پیش‌فرض: 50)

Response 200:
{
  "count": 100,
  "next": "http://localhost:8000/api/cryptocurrencies/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "coin_id": "bitcoin",
      "symbol": "btc",
      "name": "Bitcoin",
      "current_price": 45000.50,
      "price_change_24h": 2500.30,
      "price_change_percentage_24h": 5.88,
      "volume_24h": 28000000000,
      "volume_change_24h": 15.5,
      "market_cap": 880000000000,
      "rank": 1,
      "rank_score": 95.5,
      "standing": 1,
      "last_updated": "2025-01-07T10:30:00Z",
      "rank_reason": "رتبه بالا به دلیل: تغییر قیمت مثبت (85.3), حجم معاملات بالا (92.1), ثبات قیمت (78.5)"
    },
    ...
  ]
}
```

#### دریافت جزئیات یک ارز
```http
GET /api/cryptocurrencies/{id}/

Response 200:
{
  "id": 1,
  "coin_id": "bitcoin",
  "symbol": "btc",
  "name": "Bitcoin",
  "current_price": 45000.50,
  "price_change_24h": 2500.30,
  "price_change_percentage_24h": 5.88,
  "price_change_percentage_7d": 12.5,
  "price_change_percentage_30d": 25.3,
  "volume_24h": 28000000000,
  "volume_change_24h": 15.5,
  "market_cap": 880000000000,
  "market_cap_rank": 1,
  "circulating_supply": 19500000,
  "total_supply": 21000000,
  "max_supply": 21000000,
  "ath": 69000,
  "ath_change_percentage": -34.78,
  "ath_date": "2021-11-10T14:24:11.849Z",
  "atl": 67.81,
  "atl_change_percentage": 66247.89,
  "atl_date": "2013-07-06T00:00:00.000Z",
  "rank": 1,
  "rank_score": 95.5,
  "standing": 1,
  "description": "Bitcoin is a decentralized cryptocurrency...",
  "homepage": "https://bitcoin.org",
  "blockchain_site": "https://blockchain.info",
  "github_url": "https://github.com/bitcoin/bitcoin",
  "last_updated": "2025-01-07T10:30:00Z",
  "rank_reason": "..."
}
```

### Monitoring

#### دریافت وضعیت نظارت
```http
GET /api/monitoring/status/

Response 200:
{
  "is_running": true,
  "last_update": "2025-01-07T10:30:00Z",
  "next_update": "2025-01-07T10:35:00Z",
  "update_interval": 300,
  "last_error": null,
  "error_count": 0
}
```

#### شروع نظارت
```http
POST /api/monitoring/start/

Response 200:
{
  "status": "success",
  "message": "Monitoring started successfully"
}
```

#### توقف نظارت
```http
POST /api/monitoring/stop/

Response 200:
{
  "status": "success",
  "message": "Monitoring stopped successfully"
}
```

#### به‌روزرسانی دستی
```http
POST /api/monitoring/manual-update/
Timeout: 120 seconds

Response 200:
{
  "status": "success",
  "message": "Data updated successfully",
  "updated_count": 100,
  "timestamp": "2025-01-07T10:30:00Z"
}
```

### Settings

#### دریافت تنظیمات
```http
GET /api/settings/

Response 200:
{
  "id": 1,
  "api_key": "CG-xxxxxxxxxxxx",
  "top_coins_count": 100,
  "update_interval": 300,
  "data_history_days": 7,
  "price_weight": 25.0,
  "volume_weight": 20.0,
  "stability_weight": 25.0,
  "market_cap_weight": 15.0,
  "social_weight": 15.0
}
```

#### به‌روزرسانی تنظیمات
```http
PUT /api/settings/
Content-Type: application/json

{
  "top_coins_count": 150,
  "update_interval": 600,
  "price_weight": 30.0,
  "volume_weight": 25.0,
  "stability_weight": 20.0,
  "market_cap_weight": 15.0,
  "social_weight": 10.0
}

Response 200:
{
  "id": 1,
  "api_key": "CG-xxxxxxxxxxxx",
  "top_coins_count": 150,
  "update_interval": 600,
  ...
}
```

### Social Standing

#### دریافت Standing از Database
```http
GET /api/standing/

Response 200:
{
  "status": "success",
  "data": {
    "BTC": 1,
    "ETH": 2,
    "BNB": 3,
    ...
  },
  "source": "database",
  "last_update": "2025-01-07T10:00:00Z"
}
```

#### به‌روزرسانی Standing
```http
POST /api/standing/update/
Timeout: 180 seconds

Response 200:
{
  "status": "success",
  "message": "Standing data updated successfully",
  "updated_count": 100,
  "timestamp": "2025-01-07T10:30:00Z"
}
```

#### دریافت Social Data مستقیم
```http
GET /api/social/fetch/

Response 200:
{
  "status": "success",
  "indicators": [
    {
      "symbol": "BTC",
      "standing": 1,
      "score": 95.5
    },
    ...
  ],
  "source": "api",
  "cached": false,
  "timestamp": "2025-01-07T10:30:00Z"
}
```

### Error Responses

#### 400 Bad Request
```json
{
  "status": "error",
  "message": "Invalid request parameters",
  "errors": {
    "field_name": ["Error description"]
  }
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### 404 Not Found
```json
{
  "detail": "Not found."
}
```

#### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error occurred"
}
```

---

## WebSocket Communication

### اتصال به WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/coins/');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleWebSocketMessage(data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

### انواع پیام‌های WebSocket

#### 1. Coin Update (به‌روزرسانی لیست ارزها)
```json
{
  "type": "coin_update",
  "coins": [
    {
      "id": 1,
      "coin_id": "bitcoin",
      "symbol": "btc",
      "name": "Bitcoin",
      "current_price": 45000.50,
      "price_change_percentage_24h": 5.88,
      "volume_24h": 28000000000,
      "market_cap": 880000000000,
      "rank": 1,
      "rank_score": 95.5,
      "standing": 1
    },
    ...
  ]
}
```

#### 2. Status Update (به‌روزرسانی وضعیت)
```json
{
  "type": "status_update",
  "status": {
    "is_running": true,
    "last_update": "2025-01-07T10:30:00Z",
    "next_update": "2025-01-07T10:35:00Z",
    "last_error": null
  }
}
```

#### 3. Error (خطا)
```json
{
  "type": "error",
  "message": "Failed to update cryptocurrency data",
  "error_details": "Connection timeout"
}
```

### ارسال درخواست از کلاینت

```javascript
// درخواست دریافت لیست ارزها
ws.send(JSON.stringify({
  type: 'get_coins'
}));

// درخواست دریافت وضعیت
ws.send(JSON.stringify({
  type: 'get_status'
}));
```

---

## مدل‌های دیتابیس

### 1. Cryptocurrency
ذخیره اطلاعات کامل هر ارز دیجیتال

```python
class Cryptocurrency(models.Model):
    # شناسایی
    coin_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    
    # قیمت
    current_price = models.FloatField()
    price_change_24h = models.FloatField(null=True)
    price_change_percentage_24h = models.FloatField(null=True)
    price_change_percentage_7d = models.FloatField(null=True)
    price_change_percentage_30d = models.FloatField(null=True)
    
    # حجم معاملات
    volume_24h = models.FloatField(null=True)
    volume_change_24h = models.FloatField(null=True)
    
    # بازار
    market_cap = models.FloatField(null=True)
    market_cap_rank = models.IntegerField(null=True)
    circulating_supply = models.FloatField(null=True)
    total_supply = models.FloatField(null=True)
    max_supply = models.FloatField(null=True)
    
    # رکوردها
    ath = models.FloatField(null=True)  # All-Time High
    ath_change_percentage = models.FloatField(null=True)
    ath_date = models.DateTimeField(null=True)
    atl = models.FloatField(null=True)  # All-Time Low
    atl_change_percentage = models.FloatField(null=True)
    atl_date = models.DateTimeField(null=True)
    
    # رتبه‌بندی
    rank = models.IntegerField(default=0)
    rank_score = models.FloatField(default=0.0)
    standing = models.IntegerField(default=0)  # Social Standing
    
    # اطلاعات تکمیلی
    description = models.TextField(blank=True)
    homepage = models.URLField(blank=True)
    blockchain_site = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # زمان
    last_updated = models.DateTimeField(auto_now=True)
```

### 2. PriceHistory
ذخیره تاریخچه قیمت برای محاسبه ثبات

```python
class PriceHistory(models.Model):
    cryptocurrency = models.ForeignKey(
        Cryptocurrency,
        on_delete=models.CASCADE,
        related_name='price_history'
    )
    price = models.FloatField()
    volume = models.FloatField()
    price_change_24h = models.FloatField()
    price_change_percentage_24h = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

### 3. Settings
تنظیمات سیستم (Singleton)

```python
class Settings(models.Model):
    # API
    api_key = models.CharField(max_length=200)
    
    # پارامترها
    top_coins_count = models.IntegerField(default=100)
    update_interval = models.IntegerField(default=300)  # ثانیه
    data_history_days = models.IntegerField(default=7)
    
    # وزن‌های رتبه‌بندی
    price_weight = models.FloatField(default=25.0)
    volume_weight = models.FloatField(default=20.0)
    stability_weight = models.FloatField(default=25.0)
    market_cap_weight = models.FloatField(default=15.0)
    social_weight = models.FloatField(default=15.0)
```

### 4. MonitoringStatus
وضعیت نظارت سیستم (Singleton)

```python
class MonitoringStatus(models.Model):
    is_running = models.BooleanField(default=False)
    last_update = models.DateTimeField(null=True)
    last_error = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)
```

### 5. SocialAPICache
Cache برای APIهای Standing

```python
class SocialAPICache(models.Model):
    api_url = models.CharField(max_length=500, unique=True)
    last_successful_request = models.DateTimeField(null=True)
    cached_data = models.JSONField(null=True)
    
    def is_cache_valid(self):
        if not self.last_successful_request or not self.cached_data:
            return False
        cache_duration = timedelta(hours=1)
        return timezone.now() - self.last_successful_request < cache_duration
```

---

## سرویس‌های Backend

### 1. CoinGeckoService
مدیریت ارتباط با CoinGecko API

```python
class CoinGeckoService:
    @staticmethod
    def get_top_coins(limit=100):
        """دریافت لیست ارزهای برتر"""
        url = f"{BASE_URL}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': limit,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '24h,7d,30d'
        }
        # درخواست و پردازش
    
    @staticmethod
    def get_coin_details(coin_id):
        """دریافت جزئیات کامل یک ارز"""
        url = f"{BASE_URL}/coins/{coin_id}"
        params = {
            'localization': False,
            'tickers': False,
            'market_data': True,
            'community_data': False,
            'developer_data': True
        }
        # درخواست و پردازش
    
    @staticmethod
    def update_cryptocurrencies():
        """به‌روزرسانی تمام ارزها"""
        # 1. دریافت Top Coins
        # 2. دریافت Standing Data
        # 3. برای هر Coin:
        #    - دریافت جزئیات
        #    - محاسبه Volume Change
        #    - ذخیره در DB
        #    - ذخیره تاریخچه
```

### 2. StandingService
مدیریت Social Standing Data

```python
class StandingService:
    @staticmethod
    def fetch_from_api(api_url):
        """دریافت از یک API با Cache"""
        # بررسی Cache
        cache = SocialAPICache.objects.filter(api_url=api_url).first()
        if cache and cache.is_cache_valid():
            return cache.cached_data
        
        # درخواست جدید
        response = requests.get(api_url, timeout=30)
        data = response.json()
        
        # به‌روزرسانی Cache
        SocialAPICache.objects.update_or_create(
            api_url=api_url,
            defaults={
                'last_successful_request': timezone.now(),
                'cached_data': data
            }
        )
        return data
    
    @staticmethod
    def merge_indicators(indicators_1, indicators_2):
        """ادغام نتایج از دو API"""
        # اولویت با API اول
        # در صورت نبود، از API دوم استفاده
    
    @staticmethod
    def fetch_and_update_standing():
        """دریافت و به‌روزرسانی Standing در DB"""
        # Fetch با Fallback
        # به‌روزرسانی Cryptocurrency.standing
```

### 3. RankingService
محاسبه رتبه‌بندی

```python
class RankingService:
    @staticmethod
    def calculate_stability_score(crypto):
        """محاسبه Stability Score"""
        # دریافت تاریخچه
        # محاسبه Variance Score
        # محاسبه Trend Consistency
        # محاسبه Reversion Risk
        # ترکیب نمرات
    
    @staticmethod
    def normalize_*(value):
        """نرمال‌سازی معیارها"""
        # Scale به 0-100
    
    @staticmethod
    def calculate_rank_score(crypto, settings):
        """محاسبه Rank Score نهایی"""
        # نرمال‌سازی تمام معیارها
        # اعمال وزن‌ها
        # جمع وزن‌دار
    
    @staticmethod
    def update_rankings():
        """به‌روزرسانی رتبه‌بندی تمام ارزها"""
        # محاسبه Score برای همه
        # مرتب‌سازی
        # اختصاص Rank
```

### 4. SchedulerService
مدیریت وظایف زمان‌بندی شده

```python
class SchedulerService:
    scheduler = BackgroundScheduler()
    standing_scheduler = BackgroundScheduler()
    
    @staticmethod
    def update_task():
        """وظیفه اصلی به‌روزرسانی"""
        try:
            # 1. Update Cryptocurrencies
            CoinGeckoService.update_cryptocurrencies()
            
            # 2. Update Rankings
            RankingService.update_rankings()
            
            # 3. Update Status
            status.last_update = timezone.now()
            status.save()
            
            # 4. Broadcast to WebSocket clients
            broadcast_update()
            
        except Exception as e:
            broadcast_error(str(e))
    
    @staticmethod
    def start_monitoring():
        """شروع نظارت خودکار"""
        settings = Settings.get_instance()
        interval = settings.update_interval
        
        scheduler.add_job(
            update_task,
            'interval',
            seconds=interval,
            id='update_task',
            replace_existing=True
        )
        scheduler.start()
    
    @staticmethod
    def update_standing_task():
        """وظیفه به‌روزرسانی Standing (هر ساعت)"""
        StandingService.fetch_and_update_standing()
    
    @staticmethod
    def start_standing_scheduler():
        """شروع Scheduler برای Standing"""
        standing_scheduler.add_job(
            update_standing_task,
            'interval',
            hours=1,
            id='standing_task',
            replace_existing=True
        )
        standing_scheduler.start()
```

---

## ارتباطات Real-Time

### Django Channels Architecture

```python
# websocket/routing.py
websocket_urlpatterns = [
    path('ws/coins/', CoinConsumer.as_asgi()),
]

# websocket/consumers.py
class CoinConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """اتصال کلاینت"""
        await self.channel_layer.group_add(
            "coin_updates",
            self.channel_name
        )
        await self.accept()
        await self.send_initial_data()
    
    async def disconnect(self, close_code):
        """قطع اتصال"""
        await self.channel_layer.group_discard(
            "coin_updates",
            self.channel_name
        )
    
    async def coin_update(self, event):
        """ارسال به‌روزرسانی ارزها"""
        await self.send(text_data=json.dumps({
            'type': 'coin_update',
            'coins': event['coins']
        }))
    
    async def status_update(self, event):
        """ارسال به‌روزرسانی وضعیت"""
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status']
        }))
```

### Frontend WebSocket Service

```javascript
// services/websocket.js
class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.callbacks = {};
  }
  
  connect() {
    const wsUrl = this.getWebSocketUrl();
    this.ws = new ReconnectingWebSocket(wsUrl, [], {
      maxReconnectAttempts: this.maxReconnectAttempts,
      reconnectInterval: 3000
    });
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
  }
  
  handleMessage(data) {
    const { type } = data;
    if (this.callbacks[type]) {
      this.callbacks[type](data);
    }
  }
  
  on(event, callback) {
    this.callbacks[event] = callback;
  }
  
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
```

---

## راه‌اندازی و استقرار

### 1. نصب با Docker (توصیه شده)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/CoinTracker.git
cd CoinTracker

# 2. ساخت و اجرای containers
docker-compose up --build

# 3. دسترسی
# Frontend: http://localhost
# Backend API: http://localhost/api
# WebSocket: ws://localhost/ws
```

### 2. نصب Local

#### Backend
```bash
cd backend

# نصب dependencies
pip install -r requirements.txt

# ایجاد database
python manage.py migrate

# ایجاد تنظیمات اولیه
python manage.py init_settings

# اجرا
python manage.py runserver
```

#### Frontend
```bash
cd frontend

# نصب dependencies
npm install

# اجرا (Development)
npm run dev

# Build (Production)
npm run build
```

### 3. تنظیمات محیطی

#### settings.json
```json
{
  "COINGECKO_API_KEY": "CG-your-api-key-here",
  "STANDING_API_URL_1": "https://api1.example.com/indicators",
  "STANDING_API_URL_2": "https://api2.example.com/indicators"
}
```

#### Docker Environment
```yaml
# docker-compose.yml
environment:
  - DJANGO_SETTINGS_MODULE=config.settings
  - DEBUG=False
  - ALLOWED_HOSTS=yourdomain.com
```

### 4. مدیریت Database

```bash
# ایجاد migration جدید
python manage.py makemigrations

# اعمال migrations
python manage.py migrate

# ایجاد superuser
python manage.py createsuperuser

# دسترسی به Django Admin
http://localhost:8000/admin
```

### 5. Nginx Configuration

```nginx
# nginx/nginx.conf
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
    }
}
```

---

## نکات امنیتی

### 1. Authentication
- استفاده از Session-based Authentication
- CSRF Protection فعال
- Secure Cookie settings در Production

### 2. CORS Configuration
```python
# Development
CORS_ALLOW_ALL_ORIGINS = True

# Production
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

### 3. API Rate Limiting
برای محافظت از سرویس در برابر Abuse:

```python
# در settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

### 4. Environment Variables
- هرگز API Keys را در کد commit نکنید
- استفاده از `settings.json` یا Environment Variables
- فایل `.gitignore` مناسب

---

## نکات عملکرد (Performance)

### 1. Database Optimization
```python
# استفاده از select_related و prefetch_related
cryptocurrencies = Cryptocurrency.objects.select_related(
    'price_history'
).prefetch_related('related_objects')

# Indexing
class Meta:
    indexes = [
        models.Index(fields=['rank']),
        models.Index(fields=['coin_id']),
    ]
```

### 2. API Caching
- Cache برای Standing APIs: 1 ساعت
- Cache برای CoinGecko: با توجه به Rate Limits

### 3. WebSocket Optimization
- استفاده از Channel Layers برای Broadcast
- محدود کردن تعداد پیام‌های ارسالی
- Compression برای داده‌های بزرگ

### 4. Frontend Optimization
- Lazy Loading برای Components
- Memoization برای محاسبات سنگین
- Debouncing برای درخواست‌های API

---

## Troubleshooting

### مشکلات رایج و راه‌حل‌ها

#### 1. WebSocket قطع می‌شود
```javascript
// استفاده از ReconnectingWebSocket
const ws = new ReconnectingWebSocket(url, [], {
  maxReconnectAttempts: 5,
  reconnectInterval: 3000
});
```

#### 2. خطای CORS
```python
# در settings.py
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
```

#### 3. Rate Limit در CoinGecko API
- استفاده از API Key
- افزایش update_interval
- پیاده‌سازی Exponential Backoff

#### 4. دیتابیس خالی است
```bash
# اجرای به‌روزرسانی دستی
curl -X POST http://localhost:8000/api/monitoring/manual-update/
```

#### 5. Scheduler متوقف شده
```python
# Restart از Django Admin یا:
python manage.py shell
>>> from tasks.scheduler import SchedulerService
>>> SchedulerService.restart_scheduler()
```

---

## API Testing

### مثال‌هایی با cURL

```bash
# ورود
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -c cookies.txt

# دریافت لیست ارزها
curl http://localhost:8000/api/cryptocurrencies/ \
  -b cookies.txt

# شروع نظارت
curl -X POST http://localhost:8000/api/monitoring/start/ \
  -b cookies.txt

# به‌روزرسانی تنظیمات
curl -X PUT http://localhost:8000/api/settings/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "top_coins_count": 150,
    "price_weight": 30.0,
    "volume_weight": 25.0
  }'
```

### مثال با Python

```python
import requests

# Session برای نگه‌داری cookies
session = requests.Session()

# ورود
login_url = 'http://localhost:8000/api/auth/login/'
login_data = {'username': 'admin', 'password': 'admin123'}
session.post(login_url, json=login_data)

# دریافت ارزها
coins_url = 'http://localhost:8000/api/cryptocurrencies/'
response = session.get(coins_url)
coins = response.json()

print(f"Total coins: {coins['count']}")
for coin in coins['results'][:5]:
    print(f"{coin['rank']}. {coin['name']} - ${coin['current_price']}")
```

---

## توسعه آینده

### ویژگی‌های برنامه‌ریزی شده
1. **پشتیبانی از چند زبان**: انگلیسی، عربی
2. **نوتیفیکیشن**: هشدارهای تغییر قیمت
3. **تحلیل تکنیکال**: اندیکاتورها و نمودارها
4. **پورتفولیو**: مدیریت سبد سرمایه‌گذاری
5. **مقایسه**: مقایسه چندین ارز
6. **Export**: خروجی PDF و Excel
7. **API عمومی**: دسترسی عمومی به API
8. **Mobile App**: اپلیکیشن موبایل

---

## مشارکت در پروژه

### راهنمای مشارکت
1. Fork کردن repository
2. ایجاد Branch برای feature جدید
3. Commit کردن تغییرات
4. Push به Branch
5. ایجاد Pull Request

### استانداردهای Code
- PEP 8 برای Python
- ESLint برای JavaScript
- Meaningful commit messages
- Documentation برای کدهای جدید

---

## لایسنس و مجوز
این پروژه تحت لایسنس MIT منتشر شده است.

---

## تماس و پشتیبانی
- **GitHub**: [Repository Link]
- **Email**: support@cointracker.com
- **Documentation**: این فایل

---

**آخرین به‌روزرسانی**: 7 ژانویه 2025
**نسخه**: 1.0.0
