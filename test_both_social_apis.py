"""
تست مستقیم هر دو API سوشال
"""
import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API اول
API1_URL = "http://81.168.119.209:8000/standing"
API1_KEY = "FOTHB4y_kZPc08eCcwdSe19bFdYEOGm51zuw6I8V-ek"

# API دوم
API2_URL = "http://87.107.108.95:8000/standing"
API2_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

def test_api(api_url, api_key, api_name, limit=10):
    """تست یک API"""
    print(f"\n{'='*60}")
    print(f"تست {api_name}")
    print(f"{'='*60}")
    print(f"URL: {api_url}")
    print(f"API Key: {api_key[:20]}...")
    print("-" * 60)
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    params = {
        'limit': limit
    }
    
    try:
        print("در حال ارسال درخواست...")
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        print(f"کد وضعیت: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API با موفقیت پاسخ داد!")
            
            data = response.json()
            indicators = data.get('indicators', [])
            total = data.get('total', 0)
            
            print(f"\nتعداد کل indicators: {total}")
            print(f"تعداد indicators دریافتی: {len(indicators)}")
            
            if indicators:
                print("\nنمونه داده‌ها:")
                for i, indicator in enumerate(indicators[:5], 1):
                    symbol = indicator.get('symbol', 'N/A')
                    standing = indicator.get('standing', 'N/A')
                    print(f"  {i}. {symbol}: standing = {standing}")
            
            print(f"\n✅ {api_name} موفقیت‌آمیز بود!")
            return True, indicators
        else:
            print(f"❌ خطا: کد وضعیت {response.status_code}")
            print(f"پاسخ: {response.text[:500]}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ خطا: درخواست timeout شد")
        return False, None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ خطا: مشکل اتصال - {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def merge_indicators(indicators_list):
    """ترکیب داده‌های indicators از چند API"""
    merged = {}
    
    for indicators in indicators_list:
        if not indicators:
            continue
            
        for indicator in indicators:
            symbol = indicator.get('symbol', '').upper()
            standing = indicator.get('standing')
            
            if not symbol or standing is None:
                continue
            
            # اگر symbol قبلاً وجود نداشته باشد، اضافه می‌کنیم
            if symbol not in merged:
                merged[symbol] = standing
    
    return merged

def main():
    """تست هر دو API"""
    print("=" * 60)
    print("تست مستقیم هر دو API سوشال")
    print("=" * 60)
    
    limit = 20
    
    # تست API اول
    success1, indicators1 = test_api(API1_URL, API1_KEY, "API اول", limit=limit)
    
    # تست API دوم
    success2, indicators2 = test_api(API2_URL, API2_KEY, "API دوم", limit=limit)
    
    # ترکیب نتایج
    print(f"\n{'='*60}")
    print("نتیجه ترکیب داده‌ها")
    print(f"{'='*60}")
    
    if success1 or success2:
        indicators_list = []
        if indicators1:
            indicators_list.append(indicators1)
        if indicators2:
            indicators_list.append(indicators2)
        
        merged = merge_indicators(indicators_list)
        
        print(f"\nتعداد از API اول: {len(indicators1) if indicators1 else 0}")
        print(f"تعداد از API دوم: {len(indicators2) if indicators2 else 0}")
        print(f"تعداد پس از ترکیب: {len(merged)}")
        
        if merged:
            print("\nنمونه داده‌های ترکیب شده:")
            for i, (symbol, standing) in enumerate(list(merged.items())[:10], 1):
                print(f"  {i}. {symbol}: standing = {standing}")
        
        print("\n✅ تست کامل شد!")
        return True
    else:
        print("\n❌ هر دو API با خطا مواجه شدند!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
