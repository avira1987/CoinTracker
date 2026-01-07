"""
تست ساده و سریع API standing
"""
import requests
import json
import sys
import io

# تنظیم encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://87.107.108.95:8000/standing"
API_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

print("="*70)
print("تست API Standing")
print("="*70)
print(f"\nURL: {BASE_URL}")
print(f"API Key: {API_KEY[:30]}...")
print(f"\nدر حال ارسال درخواست (این ممکن است چند لحظه طول بکشد)...")

headers = {'X-API-Key': API_KEY}
params = {'limit': 10}

try:
    response = requests.get(BASE_URL, headers=headers, params=params, timeout=120)
    
    print(f"\n✅ پاسخ دریافت شد!")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        indicators = data.get('indicators', [])
        
        print(f"\n📊 داده‌های دریافت شده:")
        print(f"   تعداد: {len(indicators)}")
        print(f"   Total: {data.get('total', 'N/A')}")
        
        if indicators:
            print(f"\n📋 نمونه داده‌ها:")
            for i, ind in enumerate(indicators[:5], 1):
                print(f"   {i}. {ind.get('symbol')} - {ind.get('name')} - Standing: {ind.get('standing')}")
            
            print(f"\n✅ API کار می‌کند و داده دریافت می‌شود!")
        else:
            print(f"\n⚠️  هیچ داده‌ای دریافت نشد")
    else:
        print(f"\n❌ خطا: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print(f"\n❌ Timeout: API پاسخ نمی‌دهد (بیش از 120 ثانیه)")
    print(f"   ممکن است API در دسترس نباشد یا کند باشد")
except requests.exceptions.ConnectionError:
    print(f"\n❌ خطای اتصال: نمی‌توان به API متصل شد")
except Exception as e:
    print(f"\n❌ خطا: {str(e)}")

print("\n" + "="*70)
