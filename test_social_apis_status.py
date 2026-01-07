"""
تست وضعیت API‌های سوشال - بررسی اینکه آیا API‌ها کار می‌کنند یا نه
"""
import requests
import json
import sys
import io
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API اول
API1_URL = "http://81.168.119.209:8000/standing"
API1_KEY = "FOTHB4y_kZPc08eCcwdSe19bFdYEOGm51zuw6I8V-ek"

# API دوم
API2_URL = "http://87.107.108.95:8000/standing"
API2_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

# Backend API
BACKEND_API_URL = "http://localhost:8000/api/social/fetch/"

def test_api_direct(api_url, api_key, api_name, limit=10):
    """تست مستقیم یک API خارجی"""
    print(f"\n{'='*70}")
    print(f"🔍 تست مستقیم {api_name}")
    print(f"{'='*70}")
    print(f"URL: {api_url}")
    print(f"API Key: {api_key[:20]}...")
    print("-" * 70)
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    params = {
        'limit': limit
    }
    
    start_time = datetime.now()
    status = {
        'name': api_name,
        'url': api_url,
        'status': 'unknown',
        'response_time': None,
        'status_code': None,
        'indicators_count': 0,
        'error': None,
        'success': False
    }
    
    try:
        print("⏳ در حال ارسال درخواست...")
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        response_time = (datetime.now() - start_time).total_seconds()
        status['response_time'] = response_time
        status['status_code'] = response.status_code
        
        print(f"📊 کد وضعیت: {response.status_code}")
        print(f"⏱️  زمان پاسخ: {response_time:.2f} ثانیه")
        
        if response.status_code == 200:
            print("✅ API با موفقیت پاسخ داد!")
            
            try:
                data = response.json()
                indicators = data.get('indicators', [])
                total = data.get('total', 0)
                
                status['indicators_count'] = len(indicators)
                status['total'] = total
                status['success'] = True
                status['status'] = 'success'
                
                print(f"📈 تعداد indicators: {len(indicators)}")
                print(f"📊 تعداد کل: {total}")
                
                if indicators:
                    print("\n📋 نمونه داده‌ها (5 مورد اول):")
                    for i, indicator in enumerate(indicators[:5], 1):
                        symbol = indicator.get('symbol', 'N/A')
                        standing = indicator.get('standing', 'N/A')
                        print(f"  {i}. {symbol}: standing = {standing}")
                
                print(f"\n✅ {api_name} کار می‌کند!")
                return status
            except json.JSONDecodeError as e:
                status['error'] = f"خطا در parse کردن JSON: {str(e)}"
                status['status'] = 'json_error'
                print(f"❌ خطا در parse کردن JSON: {str(e)}")
                print(f"پاسخ خام: {response.text[:200]}")
                return status
        else:
            status['error'] = f"کد وضعیت {response.status_code}"
            status['status'] = 'http_error'
            print(f"❌ خطا: کد وضعیت {response.status_code}")
            print(f"پاسخ: {response.text[:500]}")
            return status
            
    except requests.exceptions.Timeout:
        status['error'] = "Timeout - درخواست timeout شد"
        status['status'] = 'timeout'
        print("❌ خطا: درخواست timeout شد (بیش از 30 ثانیه)")
        return status
    except requests.exceptions.ConnectionError as e:
        status['error'] = f"خطای اتصال: {str(e)}"
        status['status'] = 'connection_error'
        print(f"❌ خطا: مشکل اتصال - {str(e)}")
        return status
    except Exception as e:
        status['error'] = str(e)
        status['status'] = 'unknown_error'
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return status

def test_backend_api():
    """تست Backend API"""
    print(f"\n{'='*70}")
    print(f"🔍 تست Backend API")
    print(f"{'='*70}")
    print(f"URL: {BACKEND_API_URL}")
    print("-" * 70)
    
    status = {
        'name': 'Backend API',
        'url': BACKEND_API_URL,
        'status': 'unknown',
        'response_time': None,
        'status_code': None,
        'indicators_count': 0,
        'api1_status': None,
        'api2_status': None,
        'cache_info': None,
        'error': None,
        'success': False
    }
    
    params = {
        'limit': 10,
        'use_both': 'true'
    }
    
    start_time = datetime.now()
    
    try:
        print("⏳ در حال ارسال درخواست...")
        response = requests.get(BACKEND_API_URL, params=params, timeout=60)
        
        response_time = (datetime.now() - start_time).total_seconds()
        status['response_time'] = response_time
        status['status_code'] = response.status_code
        
        print(f"📊 کد وضعیت: {response.status_code}")
        print(f"⏱️  زمان پاسخ: {response_time:.2f} ثانیه")
        
        if response.status_code == 200:
            print("✅ Backend API با موفقیت پاسخ داد!")
            
            try:
                data = response.json()
                indicators = data.get('indicators', [])
                sources = data.get('sources', [])
                api1_count = data.get('api1_count', 0)
                api2_count = data.get('api2_count', 0)
                cache_info = data.get('cache_info', {})
                
                status['indicators_count'] = len(indicators)
                status['api1_count'] = api1_count
                status['api2_count'] = api2_count
                status['sources'] = sources
                status['cache_info'] = cache_info
                status['success'] = True
                status['status'] = 'success'
                
                print(f"📈 تعداد indicators: {len(indicators)}")
                print(f"📊 تعداد از API اول: {api1_count}")
                print(f"📊 تعداد از API دوم: {api2_count}")
                print(f"🔗 منابع: {', '.join(sources) if sources else 'هیچکدام'}")
                
                if cache_info:
                    print("\n💾 اطلاعات Cache:")
                    for api_name, cache_data in cache_info.items():
                        from_cache = cache_data.get('from_cache', False)
                        last_update = cache_data.get('last_update', 'N/A')
                        print(f"  {api_name}: {'از cache' if from_cache else 'از API'} - آخرین به‌روزرسانی: {last_update}")
                
                if indicators:
                    print("\n📋 نمونه داده‌ها (5 مورد اول):")
                    for i, indicator in enumerate(indicators[:5], 1):
                        symbol = indicator.get('symbol', 'N/A')
                        standing = indicator.get('standing', 'N/A')
                        print(f"  {i}. {symbol}: standing = {standing}")
                
                print(f"\n✅ Backend API کار می‌کند!")
                return status
            except json.JSONDecodeError as e:
                status['error'] = f"خطا در parse کردن JSON: {str(e)}"
                status['status'] = 'json_error'
                print(f"❌ خطا در parse کردن JSON: {str(e)}")
                print(f"پاسخ خام: {response.text[:200]}")
                return status
        else:
            status['error'] = f"کد وضعیت {response.status_code}"
            status['status'] = 'http_error'
            print(f"❌ خطا: کد وضعیت {response.status_code}")
            try:
                error_data = response.json()
                print(f"پیام خطا: {error_data.get('error', 'Unknown error')}")
                status['error'] = error_data.get('error', f"کد وضعیت {response.status_code}")
            except:
                print(f"پاسخ: {response.text[:500]}")
            return status
            
    except requests.exceptions.Timeout:
        status['error'] = "Timeout - درخواست timeout شد"
        status['status'] = 'timeout'
        print("❌ خطا: درخواست timeout شد (بیش از 60 ثانیه)")
        print("💡 مطمئن شوید که backend در حال اجرا است")
        return status
    except requests.exceptions.ConnectionError as e:
        status['error'] = f"خطای اتصال: {str(e)}"
        status['status'] = 'connection_error'
        print(f"❌ خطا: مشکل اتصال - {str(e)}")
        print("💡 مطمئن شوید که backend در حال اجرا است (http://localhost:8000)")
        return status
    except Exception as e:
        status['error'] = str(e)
        status['status'] = 'unknown_error'
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return status

def print_summary(results):
    """چاپ خلاصه نتایج"""
    print(f"\n{'='*70}")
    print("📊 خلاصه نتایج")
    print(f"{'='*70}")
    
    success_count = sum(1 for r in results if r.get('success', False))
    total_count = len(results)
    
    print(f"\n✅ API‌های موفق: {success_count}/{total_count}")
    print(f"❌ API‌های ناموفق: {total_count - success_count}/{total_count}")
    
    print("\n📋 جزئیات:")
    for result in results:
        name = result.get('name', 'Unknown')
        status = result.get('status', 'unknown')
        success = result.get('success', False)
        response_time = result.get('response_time')
        indicators_count = result.get('indicators_count', 0)
        error = result.get('error')
        
        status_icon = "✅" if success else "❌"
        status_text = "کار می‌کند" if success else "کار نمی‌کند"
        
        print(f"\n{status_icon} {name}: {status_text}")
        print(f"   وضعیت: {status}")
        if response_time:
            print(f"   زمان پاسخ: {response_time:.2f} ثانیه")
        if indicators_count > 0:
            print(f"   تعداد indicators: {indicators_count}")
        if error:
            print(f"   خطا: {error}")

def main():
    """تست اصلی"""
    print("=" * 70)
    print("🧪 تست وضعیت API‌های سوشال")
    print("=" * 70)
    print(f"زمان تست: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # تست API اول
    result1 = test_api_direct(API1_URL, API1_KEY, "API اول (81.168.119.209)", limit=10)
    results.append(result1)
    
    # تست API دوم
    result2 = test_api_direct(API2_URL, API2_KEY, "API دوم (87.107.108.95)", limit=10)
    results.append(result2)
    
    # تست Backend API
    result3 = test_backend_api()
    results.append(result3)
    
    # چاپ خلاصه
    print_summary(results)
    
    # نتیجه نهایی
    print(f"\n{'='*70}")
    all_success = all(r.get('success', False) for r in results)
    if all_success:
        print("✅ همه API‌ها کار می‌کنند!")
        return True
    else:
        print("⚠️  برخی API‌ها کار نمی‌کنند!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
