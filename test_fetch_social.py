"""
تست API برای دریافت مستقیم اطلاعات سوشال از هر دو API خارجی
"""
import requests
import json
import sys
import io

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api/social/fetch/"

def test_fetch_social_data(limit=10, offset=0, symbol=None, use_both=True):
    """تست دریافت مستقیم داده‌های سوشال از هر دو API"""
    print("=" * 60)
    print("تست دریافت مستقیم اطلاعات سوشال از هر دو API")
    print("=" * 60)
    print(f"URL: {BASE_URL}")
    print("-" * 60)
    
    params = {
        'limit': limit,
        'offset': offset,
        'use_both': 'true' if use_both else 'false'
    }
    
    if symbol:
        params['symbol'] = symbol
        print(f"Symbol: {symbol}")
    
    print(f"Limit: {limit}, Offset: {offset}")
    print(f"استفاده از هر دو API: {'بله' if use_both else 'خیر (فقط API اول)'}")
    print("-" * 60)
    
    try:
        print("در حال ارسال درخواست...")
        response = requests.get(BASE_URL, params=params, timeout=60)
        
        print(f"\nکد وضعیت: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API با موفقیت پاسخ داد!")
            
            data = response.json()
            indicators = data.get('indicators', [])
            total = data.get('total', 0)
            sources = data.get('sources', [])
            api1_count = data.get('api1_count', 0)
            api2_count = data.get('api2_count', 0)
            merged_count = data.get('merged_count', 0)
            
            print(f"\nمنابع داده: {', '.join(sources) if sources else 'هیچکدام'}")
            print(f"تعداد از API اول: {api1_count}")
            if use_both:
                print(f"تعداد از API دوم: {api2_count}")
            print(f"تعداد پس از ترکیب: {merged_count}")
            print(f"تعداد کل indicators: {total}")
            print(f"تعداد indicators دریافتی: {len(indicators)}")
            
            if indicators:
                print("\nنمونه داده‌ها:")
                for i, indicator in enumerate(indicators[:10], 1):
                    symbol = indicator.get('symbol', 'N/A')
                    standing = indicator.get('standing', 'N/A')
                    print(f"  {i}. {symbol}: standing = {standing}")
            
            print("\n✅ تست موفقیت‌آمیز بود!")
            return True
        else:
            print(f"❌ خطا: کد وضعیت {response.status_code}")
            try:
                error_data = response.json()
                print(f"پیام خطا: {error_data.get('error', 'Unknown error')}")
                if 'api1_status' in error_data:
                    print(f"وضعیت API اول: {error_data.get('api1_status')}")
                if 'api2_status' in error_data:
                    print(f"وضعیت API دوم: {error_data.get('api2_status')}")
            except:
                print(f"پاسخ: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ خطا: درخواست timeout شد")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ خطا: مشکل اتصال - {str(e)}")
        print("💡 مطمئن شوید که backend در حال اجرا است (http://localhost:8000)")
        return False
    except Exception as e:
        print(f"❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='تست API دریافت اطلاعات سوشال از هر دو API')
    parser.add_argument('--limit', type=int, default=10, help='تعداد نتایج (default: 10)')
    parser.add_argument('--offset', type=int, default=0, help='آفست (default: 0)')
    parser.add_argument('--symbol', type=str, default=None, help='فیلتر بر اساس symbol (مثال: BTC)')
    parser.add_argument('--use-both', action='store_true', default=True, help='استفاده از هر دو API (default: True)')
    parser.add_argument('--use-single', action='store_true', help='استفاده فقط از API اول')
    
    args = parser.parse_args()
    
    use_both = not args.use_single if args.use_single else args.use_both
    
    success = test_fetch_social_data(
        limit=args.limit, 
        offset=args.offset, 
        symbol=args.symbol,
        use_both=use_both
    )
    exit(0 if success else 1)
