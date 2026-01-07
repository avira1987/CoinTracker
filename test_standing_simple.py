"""
تست ساده برای بررسی API standing
"""
import requests
import json
import sys
import io

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://87.107.108.95:8000/standing"
API_KEY = "xl29bU5_kE8wfbEXY0w1Pyv-BpjGT3qzXwv7GEHkHqI"

def test_standing_api():
    """تست ساده API standing"""
    print("="*70)
    print("تست API Standing")
    print("="*70)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        # درخواست با limit=10
        url = f"{BASE_URL}?limit=10"
        print(f"\n📡 درخواست به: {url}")
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            indicators = data.get('indicators', [])
            
            print(f"\n✅ موفق!")
            print(f"   تعداد indicators: {len(indicators)}")
            print(f"   Total: {data.get('total', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            
            print(f"\n📋 نمونه داده‌ها:")
            for i, ind in enumerate(indicators[:5], 1):
                print(f"   {i}. {ind.get('symbol')} - {ind.get('name')} - Standing: {ind.get('standing')}")
            
            # ساخت Map
            standing_map = {}
            for ind in indicators:
                symbol = ind.get('symbol', '').upper()
                standing = ind.get('standing')
                if symbol:
                    standing_map[symbol] = standing
            
            print(f"\n🗺️  Standing Map:")
            for symbol, standing in list(standing_map.items())[:5]:
                print(f"   {symbol}: {standing}")
            
            return True
        else:
            print(f"\n❌ خطا: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_standing_api()
