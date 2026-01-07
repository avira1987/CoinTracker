"""
تست API اجتماعی با IP و کلید جدید
"""
import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://81.168.119.209:8000/standing"
API_KEY = "FOTHB4y_kZPc08eCcwdSe19bFdYEOGm51zuw6I8V-ek"

def test_social_api():
    """تست API اجتماعی"""
    print("=" * 60)
    print("تست API اجتماعی")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print("-" * 60)
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    params = {
        'limit': 10,
        'offset': 0
    }
    
    try:
        print("در حال ارسال درخواست...")
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
        
        print(f"\nکد وضعیت: {response.status_code}")
        
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
            
            print("\n✅ تست موفقیت‌آمیز بود!")
            return True
        else:
            print(f"❌ خطا: کد وضعیت {response.status_code}")
            print(f"پاسخ: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ خطا: درخواست timeout شد")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ خطا: مشکل اتصال - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_social_api()
    exit(0 if success else 1)
