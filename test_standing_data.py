"""
تست دریافت داده‌های standing از API
"""
import requests
import json
import sys
import io
from datetime import datetime

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# تنظیمات
STANDING_API_URL = "http://87.107.108.95:8000/standing"
API_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

def test_standing_data():
    """تست دریافت داده‌های standing"""
    print("="*80)
    print("تست دریافت داده‌های Standing از API")
    print("="*80)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    # تست 1: دریافت با limit=10
    print("\n" + "="*80)
    print("تست 1: دریافت 10 رکورد اول")
    print("="*80)
    
    try:
        url = f"{STANDING_API_URL}?limit=10"
        print(f"\n📡 درخواست به: {url}")
        print(f"   API Key: {API_KEY[:20]}...")
        
        response = requests.get(url, headers=headers, timeout=60)
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            indicators = data.get('indicators', [])
            
            print(f"\n✅ درخواست موفق!")
            print(f"\n📊 اطلاعات کلی:")
            print(f"   تعداد indicators: {len(indicators)}")
            print(f"   Total: {data.get('total', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            
            if indicators:
                print(f"\n📋 داده‌های دریافت شده:")
                print(f"{'='*80}")
                print(f"{'ID':<6} {'Symbol':<10} {'Name':<20} {'Standing':<12} {'Created At':<25}")
                print(f"{'-'*6} {'-'*10} {'-'*20} {'-'*12} {'-'*25}")
                
                for ind in indicators:
                    ind_id = ind.get('id', 'N/A')
                    symbol = ind.get('symbol', 'N/A')
                    name = ind.get('name', 'N/A')
                    standing = ind.get('standing', 'N/A')
                    created_at = ind.get('created_at', 'N/A')
                    
                    # کوتاه کردن نام اگر خیلی طولانی است
                    if len(name) > 18:
                        name = name[:15] + "..."
                    
                    print(f"{ind_id:<6} {symbol:<10} {name:<20} {standing:<12} {str(created_at)[:25]:<25}")
                
                # نمایش JSON کامل برای چند رکورد اول
                print(f"\n📄 JSON کامل (3 رکورد اول):")
                print(f"{'='*80}")
                print(json.dumps(indicators[:3], indent=2, ensure_ascii=False))
                
                # ساخت Map از symbol به standing
                standing_map = {}
                for ind in indicators:
                    symbol = ind.get('symbol', '').upper()
                    standing = ind.get('standing')
                    if symbol:
                        standing_map[symbol] = standing
                
                print(f"\n🗺️  Standing Map (نمونه):")
                print(f"{'='*80}")
                for symbol, standing in list(standing_map.items())[:10]:
                    print(f"   {symbol}: {standing}")
                
                return True
            else:
                print("\n⚠️  هیچ داده‌ای دریافت نشد!")
                return False
        else:
            print(f"\n❌ خطا: Status Code {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n❌ خطا: درخواست timeout شد (بیش از 60 ثانیه)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ خطا: اتصال به سرور برقرار نشد")
        print(f"   لطفاً مطمئن شوید که API در دسترس است")
        return False
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_standing_with_limit(limit=100):
    """تست دریافت با limit مشخص"""
    print("\n" + "="*80)
    print(f"تست 2: دریافت {limit} رکورد")
    print("="*80)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"{STANDING_API_URL}?limit={limit}"
        print(f"\n📡 درخواست به: {url}")
        
        response = requests.get(url, headers=headers, timeout=60)
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            indicators = data.get('indicators', [])
            
            print(f"\n✅ درخواست موفق!")
            print(f"   تعداد indicators دریافت شده: {len(indicators)}")
            print(f"   Total: {data.get('total', 'N/A')}")
            
            # آمار standing
            if indicators:
                standings = [ind.get('standing', 0) for ind in indicators if ind.get('standing')]
                if standings:
                    print(f"\n📊 آمار Standing:")
                    print(f"   حداقل: {min(standings)}")
                    print(f"   حداکثر: {max(standings)}")
                    print(f"   میانگین: {sum(standings) / len(standings):.2f}")
                
                # تعداد کوین‌های با standing بالا
                high_standing = [ind for ind in indicators if ind.get('standing', 0) > 500]
                print(f"\n📈 کوین‌های با Standing بالا (>500): {len(high_standing)}")
                for ind in high_standing[:5]:
                    print(f"   {ind.get('symbol')}: {ind.get('standing')}")
            
            return True
        else:
            print(f"\n❌ خطا: Status Code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False

def test_standing_by_symbol(symbol='BTC'):
    """تست دریافت داده برای یک symbol خاص"""
    print("\n" + "="*80)
    print(f"تست 3: دریافت داده برای {symbol}")
    print("="*80)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"{STANDING_API_URL}?limit=1&symbol={symbol}"
        print(f"\n📡 درخواست به: {url}")
        
        response = requests.get(url, headers=headers, timeout=60)
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            indicators = data.get('indicators', [])
            
            if indicators:
                ind = indicators[0]
                print(f"\n✅ داده دریافت شد:")
                print(f"   ID: {ind.get('id')}")
                print(f"   Symbol: {ind.get('symbol')}")
                print(f"   Name: {ind.get('name')}")
                print(f"   Standing: {ind.get('standing')}")
                print(f"   Created At: {ind.get('created_at')}")
                return True
            else:
                print(f"\n⚠️  هیچ داده‌ای برای {symbol} یافت نشد")
                return False
        else:
            print(f"\n❌ خطا: Status Code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        return False

def main():
    """اجرای تمام تست‌ها"""
    print("\n" + "="*80)
    print("شروع تست‌های Standing API")
    print("="*80)
    print(f"زمان شروع: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # تست 1: دریافت 10 رکورد
    results.append(("تست 1: دریافت 10 رکورد", test_standing_data()))
    
    # تست 2: دریافت 100 رکورد
    results.append(("تست 2: دریافت 100 رکورد", test_standing_with_limit(100)))
    
    # تست 3: دریافت برای BTC
    results.append(("تست 3: دریافت برای BTC", test_standing_by_symbol('BTC')))
    
    # تست 4: دریافت برای ETH
    results.append(("تست 4: دریافت برای ETH", test_standing_by_symbol('ETH')))
    
    # خلاصه نتایج
    print("\n" + "="*80)
    print("خلاصه نتایج:")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nنتیجه کلی: {passed} موفق، {failed} ناموفق از {len(results)} تست")
    print(f"زمان پایان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
